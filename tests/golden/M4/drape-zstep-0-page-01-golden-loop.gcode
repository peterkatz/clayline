; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=drape-zstep-0-page-01-golden-loop
; prepared_trace_sha256=b34034ed2499587aad35361d7f04b2826a0e8156b1afec78b966eff303c18b0f
; body_sha256=c870ece1f203a62ce75476dac46df1c21c44709f5ae359960c474b880e71f910
; profile_name=potterbot-xl
; profile_version=1.3.0
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
; stats.motion_count=27
; stats.print_motion_count=26
; stats.travel_motion_count=1
; stats.stroke_count=3
; stats.page_count=1
; stats.print_path_mm=400.124903
; stats.deposited_path_mm=389.124903
; stats.travel_path_mm=26.575365
; stats.total_motion_path_mm=426.700268
; stats.motion_time_seconds=13.116486
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=13.116486
; stats.body_volume_mm3=4740.367647
; stats.wet_weight_g=8.532662
; stats.body_e=1970.815851
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=nominal — drape mode: physical bead placement depends on fall
; parameter.alternate=true
; parameter.drape_draw=0.6
; parameter.drape_landing_mm=20
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.joint_boost=0.0
; parameter.layers=3
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_pause_seconds=disabled
; parameter.page_travel_clearance=50.0
; parameter.provisional_flow_multiplier=1.0
; parameter.split_source_page=1
; parameter.standoff_z=20
; parameter.z_mode=drape
; parameter.z_modulation=0.0
; parameter.z_step_per_layer=0
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
G1 E100 F40000 ; Prime Extruder (v1.3.0: matches the reduced end-of-job depressurize)
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
G0 X187.5 Y185 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=golden-loop note=thread launch position
G1 E97.959184 F2400 ; clayline kind=thread_launch page=0 layer=0 stroke=golden-loop note=thread launch
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=golden-page page_name=golden-loop z_mode=drape
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=golden-loop
G1 X212.5 Y185 Z20 E220.408163 F2400 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X227.5 Y200 Z20 E324.309568 F2400 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X212.5 Y220 Z20 E446.758547 F2400 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X187.5 Y215 Z20 E571.632495 F2400 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X187.5 Y185 Z20 E718.57127 F2400 ; clayline kind=print page=0 layer=0 stroke=golden-loop
; CLAYLINE_STROKE_END page=0 layer=0 id=golden-loop
; CLAYLINE_MARKER page=0 layer=1 text=layer 1 page_id=golden-page page_name=golden-loop z_mode=drape
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=golden-loop
G1 X187.5 Y215 Z20 E865.510046 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop
G1 X212.5 Y220 Z20 E990.383993 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop
G1 X227.5 Y200 Z20 E1112.832973 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop
G1 X212.5 Y185 Z20 E1216.734377 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop
G1 X187.5 Y185 Z20 E1339.183357 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop
; CLAYLINE_STROKE_END page=0 layer=1 id=golden-loop
; CLAYLINE_MARKER page=0 layer=2 text=layer 2 page_id=golden-page page_name=golden-loop z_mode=drape
; CLAYLINE_STROKE_BEGIN page=0 layer=2 id=golden-loop
G1 X212.5 Y185 Z20 E1461.632336 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop
G1 X227.5 Y200 Z20 E1565.533741 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop
G1 X212.5 Y220 Z20 E1687.982721 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop
G1 X187.5 Y215 Z20 E1812.856668 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop
G1 X187.5 Y185 Z20 E1959.795443 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop
G1 X188.5 Y185 Z20 E1961.999525 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X189.5 Y185 Z20 E1963.958709 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X190.5 Y185 Z20 E1965.672994 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X191.5 Y185 Z20 E1967.142382 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X192.5 Y185 Z20 E1968.366872 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X193.5 Y185 Z20 E1969.346464 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X194.5 Y185 Z20 E1970.081158 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X195.5 Y185 Z20 E1970.570954 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X196.5 Y185 Z20 E1970.815851 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X197.5 Y185 Z20 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
G1 X207.5 Y185 Z20 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop note=thread landing
; CLAYLINE_STROKE_END page=0 layer=2 id=golden-loop
; CLAYLINE_BODY_END
; CLAYLINE_PROFILE_END_BEGIN
M83 ;Set to Relative Extrusion Mode
G91 ;Set to Relative Positioning
G1 Z150 E-100 F40000 ;Move Z Axis up and relieve Extruder pressure (v1.3.0: was E-3000, which left the next job dry)
G90 ;Set to Absolute Positioning
G28 Z ;Home Z
G1 X207.5 Y0 F500 ;Move X and Y slow to home position
M82 ;absolute extrusion mode
; CLAYLINE_PROFILE_END_END
