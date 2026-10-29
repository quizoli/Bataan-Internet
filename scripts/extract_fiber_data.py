import zipfile
import re
import json
import math
import xml.etree.ElementTree as ET

def haversine(c1, c2):
    R = 6371.0 # km
    dlat = math.radians(c2[1] - c1[1])
    dlon = math.radians(c2[0] - c1[0])
    a = math.sin(dlat/2)**2 + math.cos(math.radians(c1[1])) * math.cos(math.radians(c2[1])) * math.sin(dlon/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def path_length(pts):
    return sum(haversine(pts[i], pts[i+1]) for i in range(len(pts)-1))

def main():
    print("Reading KMZ...")
    with zipfile.ZipFile("NATIONAL & REGIONAL BACKBONE_NOV 2024_REPORT.kmz") as z:
        with z.open("doc.kml") as f:
            content = f.read().decode("utf-8", errors="ignore")

    # fix undeclared namespace mwm
    content = re.sub(r'<kml\b([^>]*)>', r'<kml\1 xmlns:mwm="http://mapswithme.com">', content, count=1)
    
    print("Parsing XML...")
    root = ET.fromstring(content)
    ns = {"kml": "http://www.opengis.net/kml/2.2"}

    # Bataan and immediate boundary box
    # Lat: 14.30 to 14.98
    # Lon: 120.15 to 120.65
    min_lat, max_lat = 14.30, 14.98
    min_lon, max_lon = 120.15, 120.65

    parent_map = {c: p for p in root.iter() for c in p}

    features = []
    
    for pm in root.findall(".//kml:Placemark", ns):
        pm_name = pm.find("kml:name", ns)
        name = pm_name.text.strip() if pm_name is not None and pm_name.text else "Unnamed"
        desc_el = pm.find("kml:description", ns)
        desc = desc_el.text.strip() if desc_el is not None and desc_el.text else ""
        
        # Build hierarchy
        curr = pm
        hierarchy = []
        while curr in parent_map:
            curr = parent_map[curr]
            if curr.tag.endswith("Folder") or curr.tag.endswith("Document"):
                fn = curr.find("kml:name", ns)
                if fn is not None and fn.text:
                    hierarchy.append(fn.text.strip())
        folder_path = " > ".join(reversed(hierarchy))

        # Check Point
        for pt in pm.findall(".//kml:Point", ns):
            c_el = pt.find("kml:coordinates", ns)
            if c_el is not None and c_el.text:
                parts = c_el.text.strip().split(",")
                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])
                        if min_lon <= lon <= max_lon and min_lat <= lat <= max_lat:
                            features.append({
                                "geom_type": "Point",
                                "name": name,
                                "description": desc,
                                "folder": folder_path,
                                "coordinates": [lon, lat]
                            })
                    except ValueError:
                        pass

        # Check LineString
        for ls in pm.findall(".//kml:LineString", ns):
            c_el = ls.find("kml:coordinates", ns)
            if c_el is not None and c_el.text:
                raw_coords = c_el.text.strip().split()
                pts = []
                for token in raw_coords:
                    parts = token.split(",")
                    if len(parts) >= 2:
                        try:
                            pts.append((float(parts[0]), float(parts[1])))
                        except ValueError:
                            pass
                in_bbox = [p for p in pts if min_lon <= p[0] <= max_lon and min_lat <= p[1] <= max_lat]
                if len(in_bbox) > 0:
                    features.append({
                        "geom_type": "LineString",
                        "name": name,
                        "description": desc,
                        "folder": folder_path,
                        "coordinates": pts,
                        "length_km": round(path_length(pts), 3)
                    })

    print(f"Extracted {len(features)} total features in Bataan bounds.")
    
    # Save raw extracted features to JSON
    with open("bataan_extracted_features.json", "w") as out:
        json.dump(features, out, indent=2)
    print("Saved bataan_extracted_features.json")

if __name__ == "__main__":
    main()
