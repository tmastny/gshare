#!/usr/bin/env python3
import xml.etree.ElementTree as ET

def parse_xctrace_backtraces_global(xml_file):
    """
    Parse an xctrace-exported XML for <backtrace> data,
    collecting frame function (symbol) and library name.
    
    Unlike the row-by-row approach, this script collects ALL <binary id="...">
    elements globally, so <binary ref="xyz"/> references are resolved properly.
    """
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # 1) Build a global dictionary of all <binary id="..."> in the entire doc.
    #    This covers the case where a row references a binary from a different row or table.
    global_bin_by_id = {}
    for binary_elem in root.findall(".//binary[@id]"):
        bin_id = binary_elem.get("id")
        global_bin_by_id[bin_id] = binary_elem

    # 2) Iterate all <row> nodes and look for <backtrace> inside them.
    all_rows = root.findall(".//row")
    for row in all_rows:
        backtrace = row.find("backtrace")
        if backtrace is None:
            continue  # skip rows with no backtrace

        frames = backtrace.findall("frame")
        for frame_elem in frames:
            func_name = frame_elem.get("name", "unknown_function")

            # The <frame> might contain <binary> inline or ref'd
            binary_elem = frame_elem.find("binary")
            lib_name = "unknown_lib"
            if binary_elem is not None:
                # If <binary ref="XYZ">, we look up globally
                ref_id = binary_elem.get("ref")
                if ref_id:
                    real_bin_elem = global_bin_by_id.get(ref_id)
                    if real_bin_elem is not None:
                        lib_name = real_bin_elem.get("name", "unknown_lib")
                    else:
                        lib_name = f"missing_global_ref_{ref_id}"
                else:
                    # e.g. <binary id="300" name="libsystem_c.dylib" />
                    lib_name = binary_elem.get("name", "unknown_lib")

            print(f"Function: {func_name}, Library: {lib_name}")

if __name__ == "__main__":
    XML_FILE = "full_export.xml"  # Adjust path
    parse_xctrace_backtraces_global(XML_FILE)
