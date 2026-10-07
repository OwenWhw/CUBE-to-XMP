"""CUBE / Adobe RGBTable codecs, independent of the UI."""
import re
import struct
import zlib
import hashlib
import time
from html import escape

kEncodeTable = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?`'|()[]{}@%$#"


def parse_xmp(file_path):
    import xml.etree.ElementTree as ET
    root = ET.parse(file_path).getroot()
    crs = "http://ns.adobe.com/camera-raw-settings/1.0/"
    rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    name_node = root.find(f".//{{{crs}}}Name/{{{rdf}}}Alt/{{{rdf}}}li")
    title = (name_node.text or "").strip() if name_node is not None else ""
    title = title or "Extracted_LUT"
    descriptions = root.findall(f".//{{{rdf}}}Description")
    table = None
    for description in descriptions:
        digest = description.get(f"{{{crs}}}RGBTable")
        if digest and re.fullmatch(r"[0-9a-fA-F]{32}", digest):
            table = description.get(f"{{{crs}}}Table_{digest}")
            if table is not None:
                break
    if table is None:
        for description in descriptions:
            for key, value in description.attrib.items():
                if key.startswith(f"{{{crs}}}Table_") and re.fullmatch(r"[0-9a-fA-F]{32}", key.rsplit("Table_", 1)[-1]):
                    table = value
                    break
            if table is not None:
                break
    if table is None:
        raise ValueError("Valid RGBTable data not found in XMP.")
    kDecodeTable = {c: i for i, c in enumerate(kEncodeTable)}
    compressed_data = bytearray()
    val, phase = 0, 0
    for c in table:
        if c.isspace():
            continue
        if c not in kDecodeTable:
            raise ValueError("Invalid RGBTable base85 character")
        d = kDecodeTable[c]
        phase += 1
        if phase == 1: val = d
        elif phase == 2: val += d * 85
        elif phase == 3: val += d * (85 * 85)
        elif phase == 4: val += d * (85 * 85 * 85)
        elif phase == 5:
            val += d * (85 * 85 * 85 * 85)
            if val > 0xFFFFFFFF:
                raise ValueError("Invalid RGBTable base85 value")
            compressed_data.extend(struct.pack('<I', val))
            phase = 0
    if phase > 0:
        if phase == 1:
            raise ValueError("Truncated RGBTable base85 data")
        if phase == 2: compressed_data.extend(struct.pack('<B', val & 0xFF))
        elif phase == 3: compressed_data.extend(struct.pack('<H', val & 0xFFFF))
        elif phase == 4: compressed_data.extend(struct.pack('<I', val)[:3])
    if len(compressed_data) < 4:
        raise ValueError("Invalid compressed data size")
    uncompressed_size = struct.unpack('<I', compressed_data[:4])[0]
    maximum_size = 16 + 65**3 * 6 + 64
    if not 16 <= uncompressed_size <= maximum_size:
        raise ValueError("RGBTable decompressed size is out of range")
    z_data = compressed_data[4:]
    try:
        decompressor = zlib.decompressobj()
        block_data = decompressor.decompress(z_data, uncompressed_size + 1)
        if not decompressor.eof or decompressor.unconsumed_tail:
            raise ValueError("Incomplete or oversized RGBTable data")
    except zlib.error as error:
        raise ValueError("Invalid RGBTable compression") from error
    if len(block_data) != uncompressed_size:
        raise ValueError("RGBTable decompressed size mismatch")
    if len(block_data) < 16:
        raise ValueError("Invalid uncompressed data block")
    h_v1, h_v2, dims, size = struct.unpack('<4I', block_data[:16])
    if dims != 3:
        raise ValueError(f"Only 3D LUTs are supported (found {dims}D)")
    if not 2 <= size <= 65:
        raise ValueError("RGBTable grid must be between 2 and 65")
    if len(block_data) < 16 + size**3 * 6:
        raise ValueError("Truncated RGBTable sample data")
    samples = [None] * (size**3)
    nopValue = [(i * 0xFFFF + (size // 2)) // (size - 1) for i in range(size)]
    offset = 16
    for r in range(size):
        for g in range(size):
            for b in range(size):
                temp_r, temp_g, temp_b = struct.unpack('<HHH', block_data[offset:offset+6])
                offset += 6
                samples[r + g * size + b * size * size] = (
                    ((temp_r + nopValue[r]) & 0xFFFF) / 65535.0,
                    ((temp_g + nopValue[g]) & 0xFFFF) / 65535.0,
                    ((temp_b + nopValue[b]) & 0xFFFF) / 65535.0,
                )
    return title, size, samples


def build_cube(title, size, samples):
    title = str(title).replace('"', "'").replace('\r', ' ').replace('\n', ' ')
    lines = [
        f'TITLE "{title}"',
        f'LUT_3D_SIZE {size}',
        'DOMAIN_MIN 0.0 0.0 0.0',
        'DOMAIN_MAX 1.0 1.0 1.0',
        '',
    ]
    for r, g, b in samples:
        lines.append(f"{r:.6f} {g:.6f} {b:.6f}")
    return '\n'.join(lines)


def encode_zlib_base85(data: bytes) -> str:
    padded_data = data + b'\x00\x00\x00'
    encoded_chars = []
    compressed_size = len(data)
    for i in range(0, len(data), 4):
        x = struct.unpack('<I', padded_data[i:i+4])[0]
        for j in range(5):
            encoded_chars.append(kEncodeTable[x % 85])
            x //= 85
            if j > 0:
                compressed_size -= 1
                if compressed_size == 0:
                    break
    return "".join(encoded_chars)


def parse_cube(file_path):
    size = None
    title = "My LUT"
    samples = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('TITLE'):
                match = re.match(r'TITLE\s+"([^"]+)"', line)
                if match:
                    title = match.group(1)
            elif line.startswith('LUT_3D_SIZE'):
                size = int(line.split()[1])
            elif line.startswith('DOMAIN_'):
                continue
            else:
                parts = line.split()
                if len(parts) >= 3:
                    try:
                        samples.append((float(parts[0]), float(parts[1]), float(parts[2])))
                    except ValueError:
                        pass
    return title, size, samples


def interpolate_3d(samples, size, new_size=32):
    new_samples = []
    ratio = (size - 1.0) / (new_size - 1.0)

    def get_sample(r, g, b):
        r = max(0, min(size - 1, r))
        g = max(0, min(size - 1, g))
        b = max(0, min(size - 1, b))
        return samples[r + g * size + b * size * size]

    for b_idx in range(new_size):
        for g_idx in range(new_size):
            for r_idx in range(new_size):
                r_pos = r_idx * ratio
                g_pos = g_idx * ratio
                b_pos = b_idx * ratio
                r0, g0, b0 = int(r_pos), int(g_pos), int(b_pos)
                r1, g1, b1 = min(r0 + 1, size - 1), min(g0 + 1, size - 1), min(b0 + 1, size - 1)
                fr, fg, fb = r_pos - r0, g_pos - g0, b_pos - b0

                if fg >= fb and fb >= fr:
                    c0, c1, c2, c3 = (get_sample(r0, g0, b0), get_sample(r0, g1, b0),
                                       get_sample(r0, g1, b1), get_sample(r1, g1, b1))
                    w0, w1, w2, w3 = 1 - fg, fg - fb, fb - fr, fr
                elif fb > fr and fr > fg:
                    c0, c1, c2, c3 = (get_sample(r0, g0, b0), get_sample(r0, g0, b1),
                                       get_sample(r1, g0, b1), get_sample(r1, g1, b1))
                    w0, w1, w2, w3 = 1 - fb, fb - fr, fr - fg, fg
                elif fb > fg and fg >= fr:
                    c0, c1, c2, c3 = (get_sample(r0, g0, b0), get_sample(r0, g0, b1),
                                       get_sample(r0, g1, b1), get_sample(r1, g1, b1))
                    w0, w1, w2, w3 = 1 - fb, fb - fg, fg - fr, fr
                elif fr >= fg and fg > fb:
                    c0, c1, c2, c3 = (get_sample(r0, g0, b0), get_sample(r1, g0, b0),
                                       get_sample(r1, g1, b0), get_sample(r1, g1, b1))
                    w0, w1, w2, w3 = 1 - fr, fr - fg, fg - fb, fb
                elif fg > fr and fr >= fb:
                    c0, c1, c2, c3 = (get_sample(r0, g0, b0), get_sample(r0, g1, b0),
                                       get_sample(r1, g1, b0), get_sample(r1, g1, b1))
                    w0, w1, w2, w3 = 1 - fg, fg - fr, fr - fb, fb
                else:
                    c0, c1, c2, c3 = (get_sample(r0, g0, b0), get_sample(r1, g0, b0),
                                       get_sample(r1, g0, b1), get_sample(r1, g1, b1))
                    w0, w1, w2, w3 = 1 - fr, fr - fb, fb - fg, fg

                new_samples.append((
                    c0[0] * w0 + c1[0] * w1 + c2[0] * w2 + c3[0] * w3,
                    c0[1] * w0 + c1[1] * w1 + c2[1] * w2 + c3[1] * w3,
                    c0[2] * w0 + c1[2] * w1 + c2[2] * w2 + c3[2] * w3,
                ))
    return new_samples


def build_xmp(title, size, samples):
    title = escape(title)
    if size is None or not samples:
        raise ValueError("Invalid CUBE file")
    if size > 32:
        samples = interpolate_3d(samples, size, 32)
        size = 32
    nopValue = [(i * 0xFFFF + (size // 2)) // (size - 1) for i in range(size)]
    block_data = bytearray()
    block_data.extend(struct.pack('<4I', 1, 1, 3, size))
    sample_bytes = bytearray(size * size * size * 6)
    for b in range(size):
        for g in range(size):
            for r in range(size):
                cube_idx = r + g * size + b * size * size
                r_val, g_val, b_val = samples[cube_idx]
                out_idx = (r * size * size + g * size + b) * 6
                temp_r = (int(round(r_val * 65535)) - nopValue[r]) & 0xFFFF
                temp_g = (int(round(g_val * 65535)) - nopValue[g]) & 0xFFFF
                temp_b = (int(round(b_val * 65535)) - nopValue[b]) & 0xFFFF
                struct.pack_into('<HHH', sample_bytes, out_idx, temp_r, temp_g, temp_b)
    block_data.extend(sample_bytes)
    block_data.extend(struct.pack('<3I', 0, 1, 0))
    block_data.extend(struct.pack('<2d', 0.0, 2.0))
    uncompressed_size = len(block_data)
    md5_hash = hashlib.md5(block_data).hexdigest()
    uuid_str = hashlib.md5((md5_hash + str(int(time.time()))).encode('utf-8')).hexdigest().upper()
    z_data = zlib.compress(block_data, level=zlib.Z_DEFAULT_COMPRESSION)
    compressed_block = struct.pack('<I', uncompressed_size) + z_data
    encoded_str = encode_zlib_base85(compressed_block)

    return f"""<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 1.000000, 0000/00/00-00:00:00        ">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about=""
    xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
   crs:PresetType="Look"
   crs:Cluster=""
   crs:UUID="{uuid_str}"
   crs:SupportsAmount="True"
   crs:SupportsColor="True"
   crs:SupportsMonochrome="True"
   crs:SupportsHighDynamicRange="True"
   crs:SupportsNormalDynamicRange="True"
   crs:SupportsSceneReferred="True"
   crs:SupportsOutputReferred="True"
   crs:RequiresRGBTables="False"
   crs:CameraModelRestriction=""
   crs:Copyright=""
   crs:ContactInfo=""
   crs:Version="14.3"
   crs:ProcessVersion="11.0"
   crs:ConvertToGrayscale="False"
   crs:RGBTable="{md5_hash}"
   crs:Table_{md5_hash}="{encoded_str}"
   crs:HasSettings="True">
   <crs:Name>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">{title}</rdf:li>
    </rdf:Alt>
   </crs:Name>
   <crs:ShortName>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:ShortName>
   <crs:SortName>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:SortName>
   <crs:Group>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">Profiles</rdf:li>
    </rdf:Alt>
   </crs:Group>
   <crs:Description>
    <rdf:Alt>
     <rdf:li xml:lang="x-default"/>
    </rdf:Alt>
   </crs:Description>
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
"""
