; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=legacy-layout-job
; prepared_trace_sha256=40e009e6b6943a3b447e0c6037ebf525cc658e1a1bc5e2a91dc01767160e4a62
; body_sha256=1b71041d62d7e2cf2e20b28a8d196751bb1bdb59a80a4718e1ccb3e073d2c03c
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
; stats.motion_count=42
; stats.print_motion_count=38
; stats.travel_motion_count=4
; stats.stroke_count=8
; stats.page_count=2
; stats.print_path_mm=1049.442719
; stats.deposited_path_mm=1027.442719
; stats.travel_path_mm=104.111026
; stats.total_motion_path_mm=1153.553745
; stats.motion_time_seconds=33.736803
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=33.736803
; stats.body_volume_mm3=12416.470139
; stats.wet_weight_g=22.349646
; stats.body_e=5162.16842
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
; parameter.stack_page_0_z_max_mm=20.0
; parameter.stack_page_0_z_min_mm=20.0
; parameter.stack_page_1_path_start_z_mm=24.0
; parameter.stack_page_1_prior_top_mm=4.0
; parameter.stack_page_1_z_max_mm=24.0
; parameter.stack_page_1_z_min_mm=24.0
; parameter.stack_page_material_height_mm=4.0
; parameter.stack_total_height_mm=8.0
; parameter.standoff_z=20.0
; parameter.z_mode=drape
; parameter.z_modulation=0.0
; parameter.z_step_per_layer=0.0
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
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0001
G1 X247.5 Y172.5 Z20 E1774.827819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0001
G1 X237.5 Y192.5 Z20 E1884.349516 F2400 ; clayline kind=carry page=0 layer=1 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0000
G1 X237.5 Y242.5 Z20 E2129.247475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X147.5 Y242.5 Z20 E2570.063802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X148.5 Y242.5 Z20 E2572.267884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X149.5 Y242.5 Z20 E2574.227067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X150.5 Y242.5 Z20 E2575.941353 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X151.5 Y242.5 Z20 E2577.410741 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X152.5 Y242.5 Z20 E2578.63523 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X153.5 Y242.5 Z20 E2579.614822 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X154.5 Y242.5 Z20 E2580.349516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X155.5 Y242.5 Z20 E2580.839312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X156.5 Y242.5 Z20 E2581.08421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X157.5 Y242.5 Z20 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
G1 X167.5 Y242.5 Z20 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=thread landing
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0000
; CLAYLINE_PAGE index=1
G0 X167.5 Y242.5 Z28 F2400 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0000 note=inter-page clearance above completed material
G0 X147.5 Y242.5 Z28 F2400 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0000 note=inter-page XY within common stack footprint
G4 S0
G0 X147.5 Y242.5 Z24 F2400 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0000 note=inter-page approach
G1 E2679.043394 F2400 ; clayline kind=thread_launch page=1 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-legacy-layout page_name=legacy-layout z_mode=drape
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X237.5 Y242.5 Z24 E3119.85972 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X237.5 Y192.5 Z24 E3364.757679 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
G1 X247.5 Y172.5 Z24 E3474.279376 F2400 ; clayline kind=carry page=1 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X157.5 Y172.5 Z24 E3915.095703 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
; CLAYLINE_MARKER page=1 layer=1 text=layer 1 page_id=page-02-legacy-layout page_name=legacy-layout z_mode=drape
; CLAYLINE_STROKE_BEGIN page=1 layer=1 id=stroke-0001
G1 X247.5 Y172.5 Z24 E4355.912029 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0001
; CLAYLINE_STROKE_END page=1 layer=1 id=stroke-0001
G1 X237.5 Y192.5 Z24 E4465.433726 F2400 ; clayline kind=carry page=1 layer=1 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=1 id=stroke-0000
G1 X237.5 Y242.5 Z24 E4710.331685 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X147.5 Y242.5 Z24 E5151.148012 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000
G1 X148.5 Y242.5 Z24 E5153.352094 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X149.5 Y242.5 Z24 E5155.311277 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X150.5 Y242.5 Z24 E5157.025563 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X151.5 Y242.5 Z24 E5158.494951 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X152.5 Y242.5 Z24 E5159.71944 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X153.5 Y242.5 Z24 E5160.699032 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X154.5 Y242.5 Z24 E5161.433726 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X155.5 Y242.5 Z24 E5161.923522 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X156.5 Y242.5 Z24 E5162.16842 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X157.5 Y242.5 Z24 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
G1 X167.5 Y242.5 Z24 F2400 ; clayline kind=print page=1 layer=1 stroke=stroke-0000 note=thread landing
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
