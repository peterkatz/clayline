; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=missing-release-source-positive
; prepared_trace_sha256=ac2584a370ac0a31e77207f1d94950de9cbc0e57b037908d9f512aa1c5cec8bd
; body_sha256=c815f23c2ee3e8922bca833f86b67fe1a961c856da997409d3d9589316847fe2
; profile_name=potterbot-xl
; profile_version=1.2.0
; profile_verified=true
; profile_flavor=marlin
; extrusion_mode=absolute
; bead_width_mm=5
; layer_height_mm=2
; flow_multiplier=1
; wet_density_g_cm3=1.8
; prime_mm=15
; end_early_mm=0
; first_layer_z_mm=2
; speed_default_mm_s=40
; speed_first_layer_mm_s=30
; speed_travel_mm_s=40
; virtual_filament_diameter_mm=1.75
; work_bounds=17,398,12,393,0,710
; machine_envelope=0,490,0,490,0,710
; stats.motion_count=15
; stats.print_motion_count=13
; stats.travel_motion_count=2
; stats.stroke_count=1
; stats.page_count=1
; stats.print_path_mm=40
; stats.deposited_path_mm=40
; stats.travel_path_mm=38
; stats.total_motion_path_mm=78
; stats.motion_time_seconds=2.283333
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=2.283333
; stats.body_volume_mm3=508.75
; stats.wet_weight_g=0.91575
; stats.body_e=211.513671
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=calibrated centerline
; parameter.alternate=true
; parameter.collision_lift=bounded-clearance-v1
; parameter.first_layer_flow_factor=1.1
; parameter.first_layer_height=2.0
; parameter.first_layer_speed_factor=0.6
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.joint_boost=0.5
; parameter.layers=1
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_mode=stack
; parameter.page_pause_seconds=disabled
; parameter.page_travel_clearance=50.0
; parameter.provisional_flow_multiplier=1.0
; parameter.stack_job_page_count=1
; parameter.stack_page_0_datum_top_z_mm=2.0
; parameter.stack_page_0_material_z_max_mm=2.0
; parameter.stack_page_0_material_z_min_mm=2.0
; parameter.stack_page_0_nominal_path_start_z_mm=2.0
; parameter.stack_page_0_nominal_top_z_mm=2.0
; parameter.stack_page_0_path_start_z_mm=2.0
; parameter.stack_page_0_z_max_mm=2.0
; parameter.stack_page_0_z_min_mm=2.0
; parameter.stack_page_material_height_mm=2.0
; parameter.stack_total_height_mm=2.0
; parameter.standoff_z=20.0
; parameter.z_mode=calibrated
; parameter.z_modulation=0.0
; parameter.z_step_per_layer=2.0
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-00 page_name=missing-release-source-positive z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X187.5 Y202.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start XY at safe Z
G0 X187.5 Y202.5 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0000 note=stroke start vertical approach
G1 X189 Y202.5 Z2 E0.514493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X190.5 Y202.5 Z2 E2.057971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X192 Y202.5 Z2 E4.630434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X193.5 Y202.5 Z2 E8.231883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X195 Y202.5 Z2 E12.862318 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X196.5 Y202.5 Z2 E18.521738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X198 Y202.5 Z2 E25.210143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X199.5 Y202.5 Z2 E32.927534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X201 Y202.5 Z2 E41.67391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X202.5 Y202.5 Z2 E51.449271 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X212.5 Y202.5 Z2 E120.0483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X217.5 Y202.5 Z2 E142.914643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X227.5 Y202.5 Z2 E211.513671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
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
