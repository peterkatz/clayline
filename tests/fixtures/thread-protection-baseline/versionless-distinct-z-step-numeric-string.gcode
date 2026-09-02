; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=legacy-layout-job
; prepared_trace_sha256=f31724d38fa4493c16553ead736ff6d71ae97bf800983e0811954c35a8fd450a
; body_sha256=4800477ef35cd9fb4f73e92384830888fe12fcba5aff8ff8860a1e7f6784d4f2
; profile_name=potterbot-xl
; profile_version=1.2.0
; profile_verified=true
; profile_flavor=marlin
; extrusion_mode=absolute
; bead_width_mm=5
; layer_height_mm=2
; flow_multiplier=1
; wet_density_g_cm3=1.8
; prime_mm=0
; end_early_mm=0
; first_layer_z_mm=20
; speed_default_mm_s=40
; speed_first_layer_mm_s=30
; speed_travel_mm_s=40
; virtual_filament_diameter_mm=1.75
; work_bounds=17,398,12,393,0,710
; machine_envelope=0,490,0,490,0,710
; stats.motion_count=44
; stats.print_motion_count=40
; stats.travel_motion_count=4
; stats.stroke_count=8
; stats.page_count=2
; stats.print_path_mm=1051.942719
; stats.deposited_path_mm=1029.942719
; stats.travel_path_mm=102.861026
; stats.total_motion_path_mm=1154.803745
; stats.motion_time_seconds=33.768053
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=33.768053
; stats.body_volume_mm3=12445.92257
; stats.wet_weight_g=22.402661
; stats.body_e=5174.413318
; stats.pressure_e_excluded=0
; stats.warning_count=8
; nominal_label=nominal — drape mode: physical bead placement depends on fall
; stats.warning_count.open_end=8
; parameter.alternate=true
; parameter.drape_draw=0.6
; parameter.drape_landing_mm=20.0
; parameter.first_layer_height=2.0
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.joint_boost=0.0
; parameter.layers=2
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_mode=stack
; parameter.page_pause_seconds=0.0
; parameter.page_travel_clearance=50.0
; parameter.page_travel_lift=4.0
; parameter.provisional_flow_multiplier=1.0
; parameter.stack_job_page_count=2
; parameter.stack_page_0_path_start_z_mm=20.0
; parameter.stack_page_0_z_max_mm=21.25
; parameter.stack_page_0_z_min_mm=20.0
; parameter.stack_page_1_path_start_z_mm=24.0
; parameter.stack_page_1_prior_top_mm=4.0
; parameter.stack_page_1_z_max_mm=25.25
; parameter.stack_page_1_z_min_mm=24.0
; parameter.stack_page_material_height_mm=4.0
; parameter.stack_total_height_mm=8.0
; parameter.standoff_z=20.0
; parameter.z_mode=drape
; parameter.z_modulation=0.0
; parameter.z_step_per_layer=1.25
; pressure_management=profile and marked pressure blocks excluded from body volume
; thermal_policy=no heater or fan commands outside verbatim profile blocks
; CLAYLINE_HEADER_END
; CLAYLINE_PROFILE_START_BEGIN
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
M107
; CLAYLINE_PROFILE_START_END
; CLAYLINE_BODY_BEGIN
G21 ; clayline units: millimeters
G90 ; clayline absolute XYZ
M82 ; clayline absolute extrusion
G92 E0 ; clayline body extrusion origin
; CLAYLINE_PAGE index=0
G0 X147.5 Y242.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=thread launch position
G1 E97.959184 F2400 ; clayline kind=thread_launch page=0 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-01-legacy-layout page_name=legacy-layout z_mode=drape
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G1 X237.5 Y242.5 Z20 E538.77551 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.5 Y192.5 Z20 E783.673469 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G1 X247.5 Y172.5 Z20 E893.195166 F2400 ; clayline kind=carry page=0 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X157.5 Y172.5 Z20 E1334.011493 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
; CLAYLINE_MARKER page=0 layer=1 text=layer 1 page_id=page-01-legacy-layout page_name=legacy-layout z_mode=drape
G1 X157.5 Y172.5 Z21.25 E1340.133942 F2400 ; clayline kind=carry page=0 layer=1 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0001
G1 X247.5 Y172.5 Z21.25 E1780.950268 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0001
G1 X237.5 Y192.5 Z21.25 E1890.471965 F2400 ; clayline kind=carry page=0 layer=1 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0000
G1 X237.5 Y242.5 Z21.25 E2135.369924 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X147.5 Y242.5 Z21.25 E2576.186251 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.5 Y242.5 Z21.25 E2578.390332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X149.5 Y242.5 Z21.25 E2580.349516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X150.5 Y242.5 Z21.25 E2582.063802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X151.5 Y242.5 Z21.25 E2583.53319 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X152.5 Y242.5 Z21.25 E2584.757679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X153.5 Y242.5 Z21.25 E2585.737271 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X154.5 Y242.5 Z21.25 E2586.471965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X155.5 Y242.5 Z21.25 E2586.961761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X156.5 Y242.5 Z21.25 E2587.206659 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X157.5 Y242.5 Z21.25 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X167.5 Y242.5 Z21.25 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0000
; CLAYLINE_PAGE index=1
G0 X167.5 Y242.5 Z28 F2400 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0000 note=inter-page clearance above completed material
G0 X147.5 Y242.5 Z28 F2400 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0000 note=inter-page XY within common stack footprint
G4 S0
G0 X147.5 Y242.5 Z24 F2400 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0000 note=inter-page approach
G1 E2685.165843 F2400 ; clayline kind=thread_launch page=1 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-legacy-layout page_name=legacy-layout z_mode=drape
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X237.5 Y242.5 Z24 E3125.982169 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X237.5 Y192.5 Z24 E3370.880128 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
G1 X247.5 Y172.5 Z24 E3480.401825 F2400 ; clayline kind=carry page=1 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X157.5 Y172.5 Z24 E3921.218152 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
; CLAYLINE_MARKER page=1 layer=1 text=layer 1 page_id=page-02-legacy-layout page_name=legacy-layout z_mode=drape
G1 X157.5 Y172.5 Z25.25 E3927.340601 F2400 ; clayline kind=carry page=1 layer=1 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=1 id=stroke-0001
G1 X247.5 Y172.5 Z25.25 E4368.156927 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0001
; CLAYLINE_STROKE_END page=1 layer=1 id=stroke-0001
G1 X237.5 Y192.5 Z25.25 E4477.678624 F2400 ; clayline kind=carry page=1 layer=1 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=1 id=stroke-0000
G1 X237.5 Y242.5 Z25.25 E4722.576583 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X147.5 Y242.5 Z25.25 E5163.39291 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X148.5 Y242.5 Z25.25 E5165.596992 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X149.5 Y242.5 Z25.25 E5167.556175 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X150.5 Y242.5 Z25.25 E5169.270461 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X151.5 Y242.5 Z25.25 E5170.739849 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X152.5 Y242.5 Z25.25 E5171.964338 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X153.5 Y242.5 Z25.25 E5172.94393 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X154.5 Y242.5 Z25.25 E5173.678624 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X155.5 Y242.5 Z25.25 E5174.16842 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X156.5 Y242.5 Z25.25 E5174.413318 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X157.5 Y242.5 Z25.25 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X167.5 Y242.5 Z25.25 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
; CLAYLINE_STROKE_END page=1 layer=1 id=stroke-0000
; CLAYLINE_BODY_END
; CLAYLINE_PROFILE_END_BEGIN
M83 ;Set to Relative Extrusion Mode
G91 ;Set to Relative Positioning
G1 Z150 E-3000 F40000 ;Move Z Axis up and depressurize Extruder slightly
G90 ;Set to Absolute Positioning
G28 Z ;Home Z
G1 X207.5 Y0 F500 ;Move X and Y slow to home position
M82 ;absolute extrusion mode
; CLAYLINE_PROFILE_END_END
