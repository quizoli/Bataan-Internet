#!/usr/bin/env python3
import json
import re
import math

def build_map():
    with open("bataan_extracted_features.json") as f:
        features = json.load(f)

    # Classification logic
    classified_lines = []
    classified_points = []
    
    # Process Points
    for feat in features:
        if feat["geom_type"] == "Point":
            name = feat["name"].replace("\n", " ").strip()
            desc = feat["description"]
            folder = feat["folder"]
            coords = feat["coordinates"]
            
            # Determine node type & jurisdiction
            category = "Core Telecom Node"
            sub_type = "POP / Node"
            jurisdiction = "Bataan"
            
            if "ZAMBALES" in folder:
                jurisdiction = "Zambales Gateway"
            elif "PAMPANGA" in folder:
                jurisdiction = "Pampanga Gateway"
                
            if "TYPE 2" in name:
                sub_type = "Type 2 Major Distribution Hub"
            elif "TYPE 3" in name:
                sub_type = "Type 3 Intermediate Node Shelter"
            elif "TYPE 4" in name:
                sub_type = "Type 4 / 4A Local Access POP"
            elif "BP" in name:
                sub_type = "Base Point (BP) Primary Feed"
            elif "PM" in name:
                sub_type = "Pole Mount (PM) Optical Node"
                
            classified_points.append({
                "name": name,
                "type": sub_type,
                "category": category,
                "jurisdiction": jurisdiction,
                "folder": folder,
                "coordinates": coords,
                "description": desc
            })

    # Process Lines
    for feat in features:
        if feat["geom_type"] == "LineString":
            name = feat["name"].replace("\n", " ").strip()
            desc = feat["description"]
            folder = feat["folder"]
            coords = feat["coordinates"]
            length = feat["length_km"]
            f_lower = folder.lower()
            n_lower = name.lower()
            
            # Determine Layer Category
            layer_cat = "aerial"
            display_name = name
            corridor = "Aerial Backbone Distribution"
            style_color = "#00d4ff" # cyan
            dash_array = "5, 5"
            weight = 3
            
            if "handhole" in f_lower or "cictsi" in f_lower or re.match(r'^\.\d+\s*km', n_lower):
                layer_cat = "handholes"
                corridor = "Civil Microduct & Handhole Spans"
                style_color = "#ffd166" # amber yellow
                dash_array = "2, 4"
                weight = 3
                if "balanga" in f_lower:
                    display_name = f"Balanga Handhole Span ({name})"
                elif "hermosa" in f_lower:
                    display_name = f"Hermosa Handhole Span ({name})"
                elif "abucay" in f_lower:
                    display_name = f"Abucay Handhole Span ({name})"
                else:
                    display_name = f"Handhole Span ({name})"
                    
            elif "not implemented" in f_lower:
                layer_cat = "unimplemented"
                corridor = "Missing / Unbuilt Western Corridor (Bagac-Mariveles Gap)"
                style_color = "#ef476f" # crimson red
                dash_array = "8, 6"
                weight = 4
                display_name = f"Unbuilt Segment: {name}"
                
            elif "underground" in f_lower or "pipe" in n_lower or "pipe" in f_lower:
                layer_cat = "underground"
                dash_array = ""
                weight = 4
                style_color = "#ff6b35" # vibrant orange
                
                if "sanfer to hermosa" in f_lower or "san fernando to hermosa" in n_lower:
                    corridor = "San Fernando - Hermosa Underground Trunk"
                    display_name = "San Fernando to Hermosa Duct Bank"
                elif "dinalupian to orion" in f_lower or "dinalupian to orion" in n_lower:
                    corridor = "Dinalupian - Orion Roman Hwy Underground Trunk"
                    display_name = "Roman Expressway Primary Conduit (Dinalupian to Orion)"
                elif "orion to mariveles" in f_lower or "orion-mariveles" in n_lower or "orion-marivles" in f_lower:
                    corridor = "Orion - Mariveles Underground Trunk"
                    display_name = "South Peninsula Conduit (Orion to Mariveles)"
                elif "segment 44" in f_lower or "dinalupihan - olongapo" in f_lower:
                    corridor = "Segment 44 Dinalupihan - Olongapo Underground Corridor"
                    display_name = f"Segment 44 Duct / FOC ({name})"
                elif "subic bay freeport" in f_lower or "sbgp" in f_lower:
                    corridor = "Subic Bay Freeport Zone Underground Link"
                    display_name = f"SBFZ Conduit ({name})"
                else:
                    corridor = "Underground Conduit & Multi-Duct Bank"
                    display_name = f"Underground Duct: {name}"
                    
            else:
                # Aerial lines
                layer_cat = "aerial"
                style_color = "#00d4ff"
                dash_array = "5, 5"
                weight = 3
                
                if "bagac-pilar" in n_lower:
                    corridor = "Bagac - Pilar Trans-Peninsular Aerial Link"
                    display_name = "Trans-Peninsular Aerial Backbone (Pilar to Bagac)"
                elif "subic- morong" in n_lower or "subic-morong" in n_lower:
                    corridor = "Subic - Morong Aerial Link"
                    display_name = "Subic to Morong Aerial Backbone"
                elif "subic-bagac" in n_lower:
                    corridor = "Subic - Bagac Aerial Link"
                    display_name = "Subic to Bagac Aerial Backbone"
                elif "layac - olongapo" in n_lower:
                    corridor = "Layac - Olongapo Aerial Link"
                    display_name = "Layac Junction to Olongapo Aerial Trunk"
                elif "porac to dinalupian" in f_lower or "porac to dinalupian" in n_lower:
                    corridor = "Porac - Dinalupian Feeder Link"
                    display_name = f"Porac to Dinalupian Feeder ({name})"
                elif "mt.view - limay" in f_lower or "mt.view - limay" in n_lower:
                    corridor = "Mt. View - Limay Industrial Aerial Feeder"
                    display_name = "Mt. View to Limay Industrial Aerial Link"
                elif "dona to orani" in f_lower or "dona to orani" in n_lower:
                    corridor = "Doña - Orani Feeder"
                    display_name = "Doña to Orani Feeder Cable"
                else:
                    corridor = "Municipal Aerial Distribution Span"
                    display_name = f"Aerial Cable ({name})"

            classified_lines.append({
                "name": display_name,
                "raw_name": name,
                "layer_cat": layer_cat,
                "corridor": corridor,
                "folder": folder,
                "length_km": length,
                "coordinates": coords,
                "style": {
                    "color": style_color,
                    "dashArray": dash_array,
                    "weight": weight
                }
            })

    # Strategic Growth Anchors (from Lipad v5 & batFIRST write-ups)
    growth_anchors = [
        {
            "name": "Hermosa Ecozone & Industrial Park (HEIP)",
            "category": "Industrial Engine",
            "town": "Hermosa",
            "lat": 14.8415, "lon": 120.4789,
            "description": "478-hectare mixed-use industrial park developed by Science Park of the PH (ICCP Group). Major anchor locator: Sumi Wiring Systems. High demand for gigabit fiber & redundant feeds."
        },
        {
            "name": "Hermosa Central & Highlands",
            "category": "Commercial Corridor",
            "town": "Hermosa",
            "lat": 14.8250, "lon": 120.5030,
            "description": "1km commercial corridor along Roman Expressway; prime location for enterprise microduct deployment and retail fiber aggregation."
        },
        {
            "name": "Freeport Area of Bataan (FAB) Main Zone",
            "category": "Freeport & Special Ecozone",
            "town": "Mariveles",
            "lat": 14.4350, "lon": 120.4950,
            "description": "1,687-hectare freeport zone with 34,800+ workers and 84% occupancy. Special economic zone requiring mission-critical high-bandwidth connectivity and Tier 3 data center readiness."
        },
        {
            "name": "Subic Bay Freeport Zone (SBFZ) Gateway",
            "category": "Logistics & Freeport",
            "town": "Hermosa / Dinalupian Border",
            "lat": 14.8480, "lon": 120.3600,
            "description": "SBFZ Hermosa/Tipo entrance connecting Bataan to Subic port and airport logistics corridors."
        },
        {
            "name": "Petron Bataan Refinery Complex",
            "category": "Energy & Petrochemical",
            "town": "Limay",
            "lat": 14.5360, "lon": 120.6020,
            "description": "180,000 barrels/day capacity, largest crude refinery in the Philippines. Requires ultra-reliable SCADA telemetry and industrial-grade fiber rings."
        },
        {
            "name": "GNPower Dinginin & Mariveles Energy Hub",
            "category": "Critical Energy Grid",
            "town": "Mariveles",
            "lat": 14.4250, "lon": 120.5350,
            "description": "Massive baseload power hub generating roughly 12-14% of national electricity and nearly 20% of Luzon grid demand. Direct DC solar-battery nodes planned."
        },
        {
            "name": "Government Arsenal",
            "category": "Defense & Strategic Site",
            "town": "Limay",
            "lat": 14.5450, "lon": 120.5880,
            "description": "Camp General Antonio Luna, national defense manufacturing and arms reserve facility; secure sovereign fiber connectivity anchor."
        },
        {
            "name": "1 Bataan Command Center",
            "category": "Public Safety & DRRM",
            "town": "Orani",
            "lat": 14.7950, "lon": 120.5280,
            "description": "Provincial disaster risk reduction, emergency response, and multi-agency surveillance command center requiring ultra-low latency fiber trunks."
        },
        {
            "name": "Bataan Provincial Capitol & Balanga Government Center",
            "category": "Civic & Government Center",
            "town": "City of Balanga",
            "lat": 14.6833, "lon": 120.5417,
            "description": "Seat of provincial governance, One Bataan initiative headquarters, central public e-Gov services hub."
        },
        {
            "name": "Bataan New Port City / Capinpin Port",
            "category": "Maritime & Port Facility",
            "town": "Pilar / Orion",
            "lat": 14.6320, "lon": 120.5880,
            "description": "Active deep-water port terminal for Ro-Ro, commercial barges, and fast ferries to Manila Bay and Cavite."
        },
        {
            "name": "Bataan-Cavite Interlink Bridge (BCIB) Northern Landing",
            "category": "Future Mega-Infrastructure",
            "town": "Mariveles (Barangay Alas-asin)",
            "lat": 14.4550, "lon": 120.5750,
            "description": "32.15-km mega-bridge landing point connecting Bataan directly across Manila Bay to Cavite/NCR. Prime candidate for cross-bay subsea/bridge optical conduits."
        },
        {
            "name": "Hermosa-Morong Economic Access Road Corridor",
            "category": "Strategic Linear ROW",
            "town": "Hermosa to Morong",
            "lat": 14.7600, "lon": 120.3500,
            "description": "19-km DPWH access road under construction (cost ₱4.27B). Mandated Dig-Once multi-duct conduit opportunity connecting east and west Bataan."
        }
    ]

    # Municipalities metadata for quick zoom and reference
    municipalities = [
        {"name": "Hermosa", "lat": 14.8306, "lon": 120.5019, "role": "Northern Industrial & Logistics Hub (HEIP, Central)"},
        {"name": "Dinalupian", "lat": 14.8692, "lon": 120.4619, "role": "Gateway to Olongapo & Central Luzon (SCTEX)"},
        {"name": "Orani", "lat": 14.8006, "lon": 120.5372, "role": "1 Bataan Command Center, Coastal Agri-Fishery"},
        {"name": "Samal", "lat": 14.7678, "lon": 120.5433, "role": "Central Peninsula Agri-Processing Corridor"},
        {"name": "Abucay", "lat": 14.7214, "lon": 120.5361, "role": "Historic Academic & Enterprise Corridor"},
        {"name": "City of Balanga", "lat": 14.6833, "lon": 120.5417, "role": "Provincial Capital, Commercial & Academic Center"},
        {"name": "Pilar", "lat": 14.6597, "lon": 120.5606, "role": "Mt. Samat Tourism, Capinpin Port, Cross-Roads"},
        {"name": "Orion", "lat": 14.6186, "lon": 120.5800, "role": "Port of Orion, Coastal Industrial Corridor"},
        {"name": "Limay", "lat": 14.5625, "lon": 120.5975, "role": "Petron Refinery, Government Arsenal, Energy Hub"},
        {"name": "Mariveles", "lat": 14.4333, "lon": 120.4833, "role": "FAB Main Freeport, GNPower, BCIB Bridge Landing"},
        {"name": "Bagac", "lat": 14.6000, "lon": 120.3958, "role": "West Coast Eco-Tourism & Maritime Gateway"},
        {"name": "Morong", "lat": 14.6756, "lon": 120.2667, "role": "West Coast Technology, BCDA Base, Subic Border"}
    ]

    # Proposed West Coast Loop Ring Closure (Bagac to Mariveles)
    # Traced along Gov. Joaquin J. Linao Road from Bagac town proper to Mariveles
    proposed_ring_coords = [
        [120.3980, 14.6057], # Bagac POP
        [120.3920, 14.5900],
        [120.3880, 14.5750],
        [120.3850, 14.5500],
        [120.3880, 14.5300], # Saysain
        [120.3950, 14.5100],
        [120.4050, 14.4900], # Quinawan
        [120.4150, 14.4750],
        [120.4300, 14.4600], # Paysawan
        [120.4450, 14.4500],
        [120.4600, 14.4420],
        [120.4696, 14.4363]  # Mariveles MVB001 POP
    ]

    # Calculate statistics
    total_km = sum(l["length_km"] for l in classified_lines)
    ug_km = sum(l["length_km"] for l in classified_lines if l["layer_cat"] == "underground")
    aerial_km = sum(l["length_km"] for l in classified_lines if l["layer_cat"] == "aerial")
    hh_km = sum(l["length_km"] for l in classified_lines if l["layer_cat"] == "handholes")
    unimpl_km = sum(l["length_km"] for l in classified_lines if l["layer_cat"] == "unimplemented")

    print(f"Stats:")
    print(f"Total Lines: {len(classified_lines)} ({total_km:.2f} km)")
    print(f"Underground: {ug_km:.2f} km")
    print(f"Aerial: {aerial_km:.2f} km")
    print(f"Handholes: {hh_km:.2f} km")
    print(f"Unimplemented: {unimpl_km:.2f} km")
    print(f"Total Nodes: {len(classified_points)}")
    print(f"Growth Anchors: {len(growth_anchors)}")

    # Bundle all data into JSON for the web application
    data_bundle = {
        "stats": {
            "total_km": round(total_km, 2),
            "underground_km": round(ug_km, 2),
            "aerial_km": round(aerial_km, 2),
            "handholes_km": round(hh_km, 2),
            "unimplemented_km": round(unimpl_km, 2),
            "total_nodes": len(classified_points),
            "bataan_nodes": len([p for p in classified_points if p["jurisdiction"] == "Bataan"]),
            "anchors_count": len(growth_anchors),
            "municipalities_count": len(municipalities)
        },
        "lines": classified_lines,
        "points": classified_points,
        "anchors": growth_anchors,
        "municipalities": municipalities,
        "proposed_loop": {
            "name": "BatFIRST Recommended Ring Closure: Bagac - Mariveles Coastal Conduit",
            "length_km": 36.8,
            "coordinates": proposed_ring_coords,
            "description": "Critical missing link to transform the open-ended spur topology into a closed-loop resilient underground municipal fiber ring. Traverses Gov. Joaquin Linao Road, connecting the Bagac POP directly to the Mariveles Freeport POP."
        }
    }

    # Write data bundle to javascript file
    with open("bataan_fiber_data.js", "w") as f:
        f.write("const BATAAN_FIBER_DATA = " + json.dumps(data_bundle, indent=2) + ";\n")
    print("Saved bataan_fiber_data.js")

    # Generate the comprehensive HTML viewer
    html_content = generate_html(data_bundle)
    with open("bataan_fiber_map.html", "w") as f:
        f.write(html_content)
    print("Saved bataan_fiber_map.html")

def generate_html(data):
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Bataan Provincial Fiber Footprint & BatFIRST Infrastructure Map</title>
  
  <!-- Leaflet CSS -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  
  <style>
    :root {
      --bg-dark: #0f172a;
      --bg-panel: rgba(15, 23, 42, 0.92);
      --bg-card: rgba(30, 41, 59, 0.85);
      --border-color: rgba(148, 163, 184, 0.18);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent-orange: #ff7849;
      --accent-cyan: #06b6d4;
      --accent-yellow: #fbbf24;
      --accent-crimson: #f43f5e;
      --accent-green: #10b981;
      --accent-purple: #8b5cf6;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    /* Top Navigation Bar */
    header {
      background: var(--bg-panel);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-color);
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      z-index: 1000;
      box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-logo {
      width: 42px;
      height: 42px;
      background: linear-gradient(135deg, #ff7849 0%, #f43f5e 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      color: white;
      box-shadow: 0 0 16px rgba(255, 120, 73, 0.4);
    }

    .brand-title h1 {
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.3px;
      color: #fff;
    }

    .brand-title p {
      font-size: 11px;
      color: var(--text-muted);
      font-weight: 500;
    }

    .quick-stats {
      display: flex;
      gap: 18px;
      align-items: center;
    }

    .stat-pill {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 6px 14px;
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      align-items: flex-start;
    }

    .stat-label {
      font-size: 9.5px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      font-weight: 600;
    }

    .stat-val {
      font-size: 14px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Main Container */
    #container {
      flex: 1;
      position: relative;
      display: flex;
    }

    #map {
      flex: 1;
      height: 100%;
      background: #0b1120;
    }

    /* Floating Left Control Panel */
    .floating-panel {
      position: absolute;
      top: 16px;
      left: 16px;
      width: 380px;
      max-height: calc(100% - 32px);
      background: var(--bg-panel);
      backdrop-filter: blur(14px);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      box-shadow: 0 12px 36px rgba(0,0,0,0.5);
      z-index: 1000;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .panel-header {
      padding: 16px 18px 12px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .panel-title {
      font-size: 13.5px;
      font-weight: 700;
      letter-spacing: -0.2px;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .panel-content {
      padding: 14px 18px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .section-title {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 8px;
    }

    /* Layer Toggle Buttons */
    .layer-group {
      display: flex;
      flex-direction: column;
      gap: 7px;
    }

    .layer-toggle {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 9px 12px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      user-select: none;
      transition: all 0.2s ease;
    }

    .layer-toggle:hover {
      background: rgba(51, 65, 85, 0.8);
      border-color: rgba(255,255,255,0.25);
    }

    .layer-toggle.active {
      border-color: rgba(255, 120, 73, 0.5);
      background: rgba(255, 120, 73, 0.1);
    }

    .toggle-left {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .color-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      flex-shrink: 0;
    }

    .toggle-info h4 {
      font-size: 12px;
      font-weight: 600;
      color: #f1f5f9;
    }

    .toggle-info p {
      font-size: 10px;
      color: var(--text-muted);
    }

    .toggle-switch {
      position: relative;
      width: 32px;
      height: 18px;
      background: #334155;
      border-radius: 20px;
      transition: 0.2s;
    }

    .toggle-switch::after {
      content: '';
      position: absolute;
      top: 2px;
      left: 2px;
      width: 14px;
      height: 14px;
      background: #fff;
      border-radius: 50%;
      transition: 0.2s;
    }

    .layer-toggle.active .toggle-switch {
      background: var(--accent-orange);
    }

    .layer-toggle.active .toggle-switch::after {
      transform: translateX(14px);
    }

    /* Municipality Selector */
    .muni-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 5px;
    }

    .muni-btn {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      padding: 6px 4px;
      border-radius: 6px;
      color: #cbd5e1;
      font-size: 10.5px;
      font-weight: 600;
      cursor: pointer;
      text-align: center;
      transition: all 0.2s;
    }

    .muni-btn:hover {
      background: var(--accent-orange);
      color: white;
      border-color: var(--accent-orange);
    }

    /* Bottom Info Card (Drawer) */
    .info-card {
      position: absolute;
      bottom: 20px;
      right: 20px;
      width: 440px;
      background: var(--bg-panel);
      backdrop-filter: blur(16px);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      box-shadow: 0 16px 40px rgba(0,0,0,0.6);
      padding: 18px 20px;
      z-index: 1000;
      max-height: calc(100% - 40px);
      overflow-y: auto;
      transition: all 0.3s ease;
    }

    .info-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 10px;
      border-bottom: 1px solid var(--border-color);
      padding-bottom: 10px;
    }

    .info-tag {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      padding: 3px 8px;
      border-radius: 4px;
      background: rgba(255, 120, 73, 0.2);
      color: var(--accent-orange);
      letter-spacing: 0.5px;
    }

    .info-title {
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      margin-top: 4px;
    }

    .info-body {
      font-size: 12px;
      line-height: 1.55;
      color: #cbd5e1;
    }

    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 6px 0;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }

    .info-row span:first-child {
      color: var(--text-muted);
    }

    .info-row span:last-child {
      font-weight: 600;
      color: #fff;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Custom Leaflet Tooltip */
    .custom-tooltip {
      background: rgba(15, 23, 42, 0.95) !important;
      border: 1px solid var(--border-color) !important;
      border-radius: 6px !important;
      color: #fff !important;
      font-family: 'Plus Jakarta Sans', sans-serif !important;
      font-size: 11px !important;
      font-weight: 600 !important;
      padding: 5px 10px !important;
      box-shadow: 0 4px 12px rgba(0,0,0,0.5) !important;
    }
    .custom-tooltip::before {
      border-top-color: rgba(15, 23, 42, 0.95) !important;
    }

    /* Floating BatFIRST Policy Pill */
    .policy-badge {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.15));
      border: 1px solid rgba(16, 185, 129, 0.35);
      border-radius: 10px;
      padding: 10px 14px;
      font-size: 11px;
      line-height: 1.45;
      color: #a7f3d0;
    }
    .policy-badge strong {
      color: #34d399;
      display: block;
      margin-bottom: 2px;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(148, 163, 184, 0.3);
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(148, 163, 184, 0.5);
    }
  </style>
</head>
<body>

  <!-- Top Navigation Header -->
  <header>
    <div class="brand">
      <div class="brand-logo">B</div>
      <div class="brand-title">
        <h1>Bataan Provincial Fiber Footprint & BatFIRST GIS Overlay</h1>
        <p>RA 12234 (DTIP) Open-Access Concession & National Backbone Integration</p>
      </div>
    </div>

    <div class="quick-stats">
      <div class="stat-pill">
        <span class="stat-label">Total Tracked Fiber</span>
        <span class="stat-val" style="color: #38bdf8;">""" + str(data["stats"]["total_km"]) + """ km</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">Underground Trunk</span>
        <span class="stat-val" style="color: var(--accent-orange);">""" + str(data["stats"]["underground_km"]) + """ km</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">Aerial Backbone</span>
        <span class="stat-val" style="color: var(--accent-cyan);">""" + str(data["stats"]["aerial_km"]) + """ km</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">Civil Handholes</span>
        <span class="stat-val" style="color: var(--accent-yellow);">""" + str(data["stats"]["handholes_km"]) + """ km</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">Core Nodes / POPs</span>
        <span class="stat-val" style="color: var(--accent-purple);">""" + str(data["stats"]["total_nodes"]) + """ Sites</span>
      </div>
    </div>
  </header>

  <!-- Main Map Workspace -->
  <div id="container">
    <div id="map"></div>

    <!-- Floating Filter & Control Panel -->
    <div class="floating-panel">
      <div class="panel-header">
        <div class="panel-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          Fiber Footprint Layers
        </div>
        <span style="font-size: 11px; color: var(--text-muted); font-family: 'JetBrains Mono';">v2024.11</span>
      </div>

      <div class="panel-content">
        <!-- Infrastructure Layers -->
        <div>
          <div class="section-title">Network Layers</div>
          <div class="layer-group">
            <div class="layer-toggle active" id="toggle-ug" onclick="toggleLayer('underground')">
              <div class="toggle-left">
                <div class="color-dot" style="background: var(--accent-orange); box-shadow: 0 0 8px var(--accent-orange);"></div>
                <div class="toggle-info">
                  <h4>Underground Backbone Conduits</h4>
                  <p>Roman Hwy, Orion-Mariveles, San Fernando</p>
                </div>
              </div>
              <div class="toggle-switch"></div>
            </div>

            <div class="layer-toggle active" id="toggle-aerial" onclick="toggleLayer('aerial')">
              <div class="toggle-left">
                <div class="color-dot" style="background: var(--accent-cyan); box-shadow: 0 0 8px var(--accent-cyan);"></div>
                <div class="toggle-info">
                  <h4>Aerial Backbone FOC</h4>
                  <p>Bagac-Pilar, Subic-Morong, Regional Trunks</p>
                </div>
              </div>
              <div class="toggle-switch"></div>
            </div>

            <div class="layer-toggle active" id="toggle-hh" onclick="toggleLayer('handholes')">
              <div class="toggle-left">
                <div class="color-dot" style="background: var(--accent-yellow); box-shadow: 0 0 8px var(--accent-yellow);"></div>
                <div class="toggle-info">
                  <h4>Handhole-to-Handhole Civil Runs</h4>
                  <p>Detailed ~300-500m Balanga, Hermosa, Abucay</p>
                </div>
              </div>
              <div class="toggle-switch"></div>
            </div>

            <div class="layer-toggle active" id="toggle-proposed" onclick="toggleLayer('proposed')">
              <div class="toggle-left">
                <div class="color-dot" style="background: var(--accent-crimson); box-shadow: 0 0 8px var(--accent-crimson);"></div>
                <div class="toggle-info">
                  <h4>BatFIRST Ring Closure (Gap Solution)</h4>
                  <p>Bagac - Mariveles 36.8km Coastal Conduit</p>
                </div>
              </div>
              <div class="toggle-switch"></div>
            </div>

            <div class="layer-toggle active" id="toggle-nodes" onclick="toggleLayer('nodes')">
              <div class="toggle-left">
                <div class="color-dot" style="background: var(--accent-purple); box-shadow: 0 0 8px var(--accent-purple);"></div>
                <div class="toggle-info">
                  <h4>Telecom POPs & Node Shelters</h4>
                  <p>Type 2/3/4A shelters, PM pole mounts, Base Points</p>
                </div>
              </div>
              <div class="toggle-switch"></div>
            </div>

            <div class="layer-toggle active" id="toggle-anchors" onclick="toggleLayer('anchors')">
              <div class="toggle-left">
                <div class="color-dot" style="background: var(--accent-green); box-shadow: 0 0 8px var(--accent-green);"></div>
                <div class="toggle-info">
                  <h4>Growth Engines & Demand Anchors</h4>
                  <p>FAB, HEIP, Petron, GNPower, Command Center</p>
                </div>
              </div>
              <div class="toggle-switch"></div>
            </div>
          </div>
        </div>

        <!-- Strategic Context -->
        <div class="policy-badge">
          <strong>RA 12234 (Konektadong Pinoy Act)</strong>
          Middle-mile passive infrastructure (trenching, conduits, handholes) funded by government CapEx under statutory "Dig-Once" doctrine. Open access leased to retail ISPs via FRAND tariffs.
        </div>

        <!-- Municipalities Quick Zoom -->
        <div>
          <div class="section-title">Jump to Municipality (11 LGUs + 1 City)</div>
          <div class="muni-grid" id="muni-buttons">
            <!-- Injected via JS -->
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Detail Drawer -->
    <div class="info-card" id="detail-card">
      <div class="info-header">
        <div>
          <span class="info-tag" id="card-tag">Strategic Overview</span>
          <h3 class="info-title" id="card-title">Bataan Provincial Backbone Infrastructure</h3>
        </div>
        <button onclick="resetCard()" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:16px;">✕</button>
      </div>
      <div class="info-body" id="card-body">
        <p style="margin-bottom: 10px;">
          Click on any fiber route, node marker, or economic anchor on the map to inspect its technical specifications, physical alignment, and connectivity mandate.
        </p>
        <div class="info-row">
          <span>Primary North-South Trunk:</span>
          <span>Roman Superhighway (Dual UG)</span>
        </div>
        <div class="info-row">
          <span>East-West Penetration:</span>
          <span>JASA / Olongapo-Gapan Road</span>
        </div>
        <div class="info-row">
          <span>Trans-Peninsular Span:</span>
          <span>Pilar - Bagac Aerial Link</span>
        </div>
        <div class="info-row">
          <span>Topology Vulnerability:</span>
          <span style="color: var(--accent-crimson);">Bagac - Mariveles Spur Gap</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Leaflet JS -->
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <!-- Embedded Data -->
  <script src="bataan_fiber_data.js"></script>

  <script>
    // Initialize Leaflet Map centered on Bataan Peninsula
    const map = L.map('map', {
      center: [14.65, 120.45],
      zoom: 11,
      zoomControl: false,
      attributionControl: false
    });

    // Custom Zoom Control top-right
    L.control.zoom({ position: 'topright' }).addTo(map);

    // Basemaps
    const esriStreet = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19
    }).addTo(map);

    const esriSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19
    });

    const esriDark = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19
    }).addTo(map);

    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19
    });

    const esriSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19
    });

    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19
    });

    const baseMaps = {
      "ESRI World Street Map (Clear Bataan Roads)": esriStreet,
      "ESRI High-Res Satellite": esriSat,
      "ESRI Dark Gray (NOC Mode)": esriDark,
      "OpenStreetMap Standard": osm
    };
    L.control.layers(baseMaps, null, { position: 'topright' }).addTo(map);

    // Feature Groups
    const layers = {
      underground: L.featureGroup().addTo(map),
      aerial: L.featureGroup().addTo(map),
      handholes: L.featureGroup().addTo(map),
      unimplemented: L.featureGroup().addTo(map),
      proposed: L.featureGroup().addTo(map),
      nodes: L.featureGroup().addTo(map),
      anchors: L.featureGroup().addTo(map)
    };

    // Render Lines
    BATAAN_FIBER_DATA.lines.forEach(line => {
      const latlngs = line.coordinates.map(pt => [pt[1], pt[0]]);
      const cat = line.layer_cat;
      const targetGroup = layers[cat] || layers.aerial;
      
      const poly = L.polyline(latlngs, {
        color: line.style.color,
        weight: line.style.weight,
        dashArray: line.style.dashArray,
        opacity: cat === 'underground' ? 0.95 : 0.85
      });

      poly.bindTooltip(`<b>${line.name}</b><br>${line.length_km} km`, {
        className: 'custom-tooltip',
        sticky: true
      });

      poly.on('click', () => {
        showLineDetails(line);
      });

      targetGroup.addLayer(poly);
    });

    // Render Proposed Resiliency Ring Closure (Bagac to Mariveles)
    const proposed = BATAAN_FIBER_DATA.proposed_loop;
    const proposedLatLngs = proposed.coordinates.map(pt => [pt[1], pt[0]]);
    const proposedPoly = L.polyline(proposedLatLngs, {
      color: '#f43f5e',
      weight: 5,
      dashArray: '10, 8',
      opacity: 0.95
    });
    proposedPoly.bindTooltip(`<b>${proposed.name}</b><br>${proposed.length_km} km (Proposed Ring Closure)`, {
      className: 'custom-tooltip',
      sticky: true
    });
    proposedPoly.on('click', () => {
      showProposedDetails(proposed);
    });
    layers.proposed.addLayer(proposedPoly);

    // Custom Icons
    function createNodeIcon(type, color) {
      return L.divIcon({
        className: 'custom-node-icon',
        html: `<div style="
          width: 14px;
          height: 14px;
          background: ${color};
          border: 2px solid #ffffff;
          border-radius: 50%;
          box-shadow: 0 0 10px ${color};
        "></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7]
      });
    }

    function createAnchorIcon(category) {
      let iconSymbol = '⚡';
      let bgCol = '#10b981';
      if (category.includes('Industrial') || category.includes('Freeport')) {
        iconSymbol = '🏭';
        bgCol = '#3b82f6';
      } else if (category.includes('Energy')) {
        iconSymbol = '⚡';
        bgCol = '#f59e0b';
      } else if (category.includes('Public Safety') || category.includes('Civic')) {
        iconSymbol = '🏛️';
        bgCol = '#8b5cf6';
      } else if (category.includes('Maritime') || category.includes('Future')) {
        iconSymbol = '🚢';
        bgCol = '#ec4899';
      }

      return L.divIcon({
        className: 'custom-anchor-icon',
        html: `<div style="
          width: 26px;
          height: 26px;
          background: rgba(15, 23, 42, 0.9);
          border: 2px solid ${bgCol};
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 13px;
          box-shadow: 0 0 12px ${bgCol};
          cursor: pointer;
        ">${iconSymbol}</div>`,
        iconSize: [26, 26],
        iconAnchor: [13, 13]
      });
    }

    // Render Telecom Nodes
    BATAAN_FIBER_DATA.points.forEach(pt => {
      const lat = pt.coordinates[1];
      const lon = pt.coordinates[0];
      const isBataan = pt.jurisdiction === 'Bataan';
      const nodeCol = isBataan ? '#8b5cf6' : '#64748b';
      
      const marker = L.marker([lat, lon], {
        icon: createNodeIcon(pt.type, nodeCol)
      });

      marker.bindTooltip(`<b>${pt.name}</b><br>${pt.type} (${pt.jurisdiction})`, {
        className: 'custom-tooltip'
      });

      marker.on('click', () => {
        showNodeDetails(pt);
      });

      layers.nodes.addLayer(marker);
    });

    // Render Growth Anchors
    BATAAN_FIBER_DATA.anchors.forEach(anc => {
      const marker = L.marker([anc.lat, anc.lon], {
        icon: createAnchorIcon(anc.category)
      });

      marker.bindTooltip(`<b>${anc.name}</b><br>${anc.category} (${anc.town})`, {
        className: 'custom-tooltip'
      });

      marker.on('click', () => {
        showAnchorDetails(anc);
      });

      layers.anchors.addLayer(marker);
    });

    // Populate Municipalities Buttons
    const muniGrid = document.getElementById('muni-buttons');
    BATAAN_FIBER_DATA.municipalities.forEach(muni => {
      const btn = document.createElement('button');
      btn.className = 'muni-btn';
      btn.innerText = muni.name;
      btn.onclick = () => {
        map.flyTo([muni.lat, muni.lon], 13.5, { duration: 1.2 });
        showMuniDetails(muni);
      };
      muniGrid.appendChild(btn);
    });

    // UI Toggle Handlers
    function toggleLayer(layerKey) {
      const toggleEl = document.getElementById(`toggle-${layerKey}`);
      const layerGroup = layers[layerKey];
      if (map.hasLayer(layerGroup)) {
        map.removeLayer(layerGroup);
        toggleEl.classList.remove('active');
      } else {
        map.addLayer(layerGroup);
        toggleEl.classList.add('active');
      }
    }

    // Details Drawer Display Functions
    function showLineDetails(line) {
      document.getElementById('card-tag').innerText = line.corridor;
      document.getElementById('card-tag').style.background = line.style.color + '22';
      document.getElementById('card-tag').style.color = line.style.color;
      document.getElementById('card-title').innerText = line.name;

      let typeDesc = "Underground Concrete Encased Microduct Bundle (4-Way 14/10mm)";
      if (line.layer_cat === 'aerial') {
        typeDesc = "Heavy Duty Aerial Figure-8 Self-Supporting Optical Cable";
      } else if (line.layer_cat === 'handholes') {
        typeDesc = "Pre-cast Composite Handholes every 300m-500m with Dual Conduits";
      }

      document.getElementById('card-body').innerHTML = `
        <div class="info-row">
          <span>Corridor Group:</span>
          <span>${line.corridor}</span>
        </div>
        <div class="info-row">
          <span>Segment Length:</span>
          <span>${line.length_km} km</span>
        </div>
        <div class="info-row">
          <span>Infrastructure Type:</span>
          <span>${line.layer_cat.toUpperCase()}</span>
        </div>
        <div class="info-row">
          <span>Technical Spec:</span>
          <span style="font-size: 11px;">${typeDesc}</span>
        </div>
        <div class="info-row">
          <span>Source Folder:</span>
          <span style="font-size: 10px; max-width: 230px; text-align: right; overflow:hidden; text-overflow:ellipsis;">${line.folder.split(' > ').slice(-2).join(' > ')}</span>
        </div>
        <div style="margin-top: 12px; font-size: 11px; color: var(--text-muted); background: rgba(0,0,0,0.25); padding: 8px 10px; border-radius: 6px;">
          <strong>BatFIRST Concession Note:</strong> Civil works co-located with road alignments (DPWH/LGU) reduce trenching costs by over 70%. Open-access microduct reservation guarantees shared tenancy for PLDT, Globe, DITO, and local micro-ISPs.
        </div>
      `;
    }

    function showProposedDetails(prop) {
      document.getElementById('card-tag').innerText = "Resiliency Ring Mandate";
      document.getElementById('card-tag').style.background = "rgba(244, 63, 94, 0.25)";
      document.getElementById('card-tag').style.color = "#f43f5e";
      document.getElementById('card-title').innerText = prop.name;

      document.getElementById('card-body').innerHTML = `
        <p style="margin-bottom: 10px; color: #fecdd3;">${prop.description}</p>
        <div class="info-row">
          <span>Alignment:</span>
          <span>Gov. Joaquin Linao Road</span>
        </div>
        <div class="info-row">
          <span>Required Civil Trenching:</span>
          <span>36.8 km</span>
        </div>
        <div class="info-row">
          <span>Topology Upgrade:</span>
          <span>Open Spur ➔ Self-Healing Ring</span>
        </div>
        <div class="info-row">
          <span>Sub-second Failover:</span>
          <span>Automatic Rerouting via West Coast</span>
        </div>
        <div style="margin-top: 12px; font-size: 11px; color: #a7f3d0; background: rgba(16, 185, 129, 0.15); padding: 8px 10px; border-radius: 6px;">
          <strong>Strategic Recommendation:</strong> Prioritize this segment under the DPWH/One Bataan Dig-Once road modernization to achieve closed-loop underground ring redundancy before typhoon season.
        </div>
      `;
    }

    function showNodeDetails(node) {
      document.getElementById('card-tag').innerText = "Telecom Point of Presence";
      document.getElementById('card-tag').style.background = "rgba(139, 92, 246, 0.25)";
      document.getElementById('card-tag').style.color = "#c084fc";
      document.getElementById('card-title').innerText = node.name;

      document.getElementById('card-body').innerHTML = `
        <div class="info-row">
          <span>Shelter Class:</span>
          <span>${node.type}</span>
        </div>
        <div class="info-row">
          <span>Jurisdiction:</span>
          <span>${node.jurisdiction}</span>
        </div>
        <div class="info-row">
          <span>Coordinates:</span>
          <span>${node.coordinates[1].toFixed(4)}°N, ${node.coordinates[0].toFixed(4)}°E</span>
        </div>
        <div class="info-row">
          <span>Power Resilience:</span>
          <span>Direct 48V DC Solar-Battery Bus (Target)</span>
        </div>
        <div style="margin-top: 12px; font-size: 11px; color: var(--text-muted); background: rgba(0,0,0,0.25); padding: 8px 10px; border-radius: 6px;">
          <strong>Node Functions:</strong> Acts as an open-access Carrier Neutral Aggregation Hub (CNAH) where local micro-ISPs connect into the high-speed middle-mile transport grid via FRAND wheeling tariffs.
        </div>
      `;
    }

    function showAnchorDetails(anc) {
      document.getElementById('card-tag').innerText = anc.category;
      document.getElementById('card-tag').style.background = "rgba(16, 185, 129, 0.25)";
      document.getElementById('card-tag').style.color = "#34d399";
      document.getElementById('card-title').innerText = anc.name;

      document.getElementById('card-body').innerHTML = `
        <p style="margin-bottom: 10px; color: #e2e8f0;">${anc.description}</p>
        <div class="info-row">
          <span>Municipality:</span>
          <span>${anc.town}</span>
        </div>
        <div class="info-row">
          <span>Strategic Role:</span>
          <span>Anchor Off-Take & High-Bandwidth Node</span>
        </div>
        <div class="info-row">
          <span>Economic Sector:</span>
          <span>${anc.category}</span>
        </div>
        <div style="margin-top: 12px; font-size: 11px; color: #bae6fd; background: rgba(56, 189, 248, 0.15); padding: 8px 10px; border-radius: 6px;">
          <strong>Off-Take Anchor:</strong> High industrial concentration de-risks private concessionaire capital by guaranteeing 5-10 year dark fiber IRU and capacity leasing revenue.
        </div>
      `;
    }

    function showMuniDetails(muni) {
      document.getElementById('card-tag').innerText = "Municipality View";
      document.getElementById('card-tag').style.background = "rgba(59, 130, 246, 0.25)";
      document.getElementById('card-tag').style.color = "#60a5fa";
      document.getElementById('card-title').innerText = muni.name;

      document.getElementById('card-body').innerHTML = `
        <div class="info-row">
          <span>Strategic Focus:</span>
          <span style="font-size: 11px; max-width: 240px; text-align: right;">${muni.role}</span>
        </div>
        <div class="info-row">
          <span>Coordinates:</span>
          <span>${muni.lat.toFixed(4)}°N, ${muni.lon.toFixed(4)}°E</span>
        </div>
        <div class="info-row">
          <span>Local Deployment:</span>
          <span>Curbside micro-trenching & Dig-Once ducts</span>
        </div>
        <div style="margin-top: 10px; font-size: 11px; color: var(--text-muted);">
          Use the layer toggles on the left to inspect underground trunks, aerial distribution spans, and nearby Points of Presence within ${muni.name}.
        </div>
      `;
    }

    function resetCard() {
      document.getElementById('card-tag').innerText = "Strategic Overview";
      document.getElementById('card-tag').style.background = "rgba(255, 120, 73, 0.2)";
      document.getElementById('card-tag').style.color = "var(--accent-orange)";
      document.getElementById('card-title').innerText = "Bataan Provincial Backbone Infrastructure";
      document.getElementById('card-body').innerHTML = `
        <p style="margin-bottom: 10px;">
          Click on any fiber route, node marker, or economic anchor on the map to inspect its technical specifications, physical alignment, and connectivity mandate.
        </p>
        <div class="info-row">
          <span>Primary North-South Trunk:</span>
          <span>Roman Superhighway (Dual UG)</span>
        </div>
        <div class="info-row">
          <span>East-West Penetration:</span>
          <span>JASA / Olongapo-Gapan Road</span>
        </div>
        <div class="info-row">
          <span>Trans-Peninsular Span:</span>
          <span>Pilar - Bagac Aerial Link</span>
        </div>
        <div class="info-row">
          <span>Topology Vulnerability:</span>
          <span style="color: var(--accent-crimson);">Bagac - Mariveles Spur Gap</span>
        </div>
      `;
    }
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    build_map()
