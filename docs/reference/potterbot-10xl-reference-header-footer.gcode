; === Clayline reference: PotterBot 10 XL ground truth ===
; Source: CFFFP_DripperWarp2.gcode — sliced with Cura 4.11 ('3D Potter 5mm' profile),
;         printed successfully by Pete on his PotterBot 10 XL (Jan 2026).
; Full file: CFFFP_DripperWarp2.gcode (maintainer's copy, not committed)
; Derived E-model: dE/dist ~= 3.118 for 5.0mm x 1.5mm bead => virtual filament dia 1.75mm (Cura standard).
;
; --- HEADER (first 25 lines) ---
;FLAVOR:Marlin
;TIME:361
;Filament used: 44.165m
;Layer height: 1.5
;MINX:136.369
;MINY:127.708
;MINZ:1.5
;MAXX:278.647
;MAXY:277.311
;MAXZ:63.801
;Generated with Cura_SteamEngine 4.11.0
M105
M109 S0
M82 ;absolute extrusion mode
G28 ;Home
G1 X207.5 Y202.5 Z20 F10000 ;Move X and Y to center, Z to 20mm high
G92 E0
G1 E3000 F40000 ; Prine Extruder
G92 E0
G92 E0
G92 E0
;LAYER_COUNT:42
;LAYER:0
M107
;MESH:DripperWarp2.obj
;
; --- EXTRUSION SAMPLE (first five body moves, for the M2 reproduction test) ---
; The G0 establishes the starting XY. E is absolute and was reset to zero above.
G0 F2400 X155.844 Y148.14 Z1.5
G1 X155.759 Y147.509 E1.98532
G1 X155.844 Y147.524 E2.25445
G1 X157.85 Y147.996 E8.68025
G1 X157.933 Y147.894 E9.0903
G1 X158.621 Y147.971 E11.24897
;
; --- FOOTER (last 33 lines) ---
G1 X206.316 Y192.817
;TIME_ELAPSED:361.630853
M83 ;Set to Relative Extrusion Mode
G91 ;Set to Relative Positioning
G1 Z150 E-3000 F40000 ;Move Z Axis up and depressurize Extruder slightly
G90 ;Set to Absolute Positioning
G28 Z ;Home Z
G1 X207.5 Y0 F500 ;Move X and Y slow to home position
M82 ;absolute extrusion mode
;End of Gcode
;SETTING_3 {"global_quality": "[general]\\nversion = 4\\nname = 3D Potter 5mm\\n
;SETTING_3 definition = custom\\n\\n[metadata]\\ntype = quality_changes\\nqualit
;SETTING_3 y_type = normal\\nsetting_version = 17\\n\\n[values]\\nadhesion_type
;SETTING_3 = none\\nlayer_height = 1.5\\nlayer_height_0 = 1.5\\nmagic_spiralize
;SETTING_3 = True\\nspeed_slowdown_layers = 0\\n\\n", "extruder_quality": ["[gen
;SETTING_3 eral]\\nversion = 4\\nname = 3D Potter 5mm\\ndefinition = custom\\n\\
;SETTING_3 n[metadata]\\ntype = quality_changes\\nquality_type = normal\\nintent
;SETTING_3 _category = default\\nposition = 0\\nsetting_version = 17\\n\\n[value
;SETTING_3 s]\\nbottom_layers = 0\\nbottom_thickness = 5\\nbrim_line_count = 1\\
;SETTING_3 nbrim_width = 0\\ncool_fan_enabled = False\\ncool_min_layer_time = 1\
;SETTING_3 \ndefault_material_print_temperature = 0\\ninfill_sparse_density = 0\
;SETTING_3 \nlayer_start_x = 205\\nlayer_start_y = 200\\nmaterial_final_print_te
;SETTING_3 mperature = 0\\nmaterial_initial_print_temperature = 0\\nretraction_a
;SETTING_3 mount = 1000\\nretraction_enable = False\\nretraction_extra_prime_amo
;SETTING_3 unt = -30\\nretraction_extrusion_window = 10\\nretraction_hop = 2\\nr
;SETTING_3 etraction_hop_enabled = True\\nretraction_min_travel = =line_width *
;SETTING_3 2\\nretraction_speed = 1000\\nskirt_gap = 10\\nskirt_line_count = 1\\
;SETTING_3 nspeed_layer_0 = 30\\nspeed_print = 40\\nspeed_travel = =speed_print
;SETTING_3 if magic_spiralize else 120\\nspeed_wall = 40\\nspeed_wall_x = 30\\nt
;SETTING_3 op_bottom_thickness = 1.5\\ntop_layers = 0\\ntop_thickness = 5\\nwall
;SETTING_3 _0_wipe_dist = 0\\nwall_thickness = 5\\nz_seam_corner = z_seam_corner
;SETTING_3 _none\\nz_seam_type = shortest\\nz_seam_x = 220\\nz_seam_y = 0\\n\\n"
;SETTING_3 ]}

; Aggregate sample: dE/sum(XY distance) = 3.118137738456385 E/mm.
; Profile formula for a 5.0 x 1.5 mm bead and virtual filament diameter 1.75 mm:
; 7.5 / (pi * (1.75/2)^2) = 3.118137660575909 E/mm.
