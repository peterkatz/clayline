; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=crossing
; prepared_trace_sha256=22669d68e2d04ae1ab8b2d7aa4c21f5e18e2b0dca652867d1d7335540e0aa89a
; body_sha256=8ea6e4aa3dd6a7f0588b9630dc919a4ca8f85ad412d51d778996e933128f2461
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
; end_early_mm=5
; first_layer_z_mm=2
; speed_default_mm_s=40
; speed_first_layer_mm_s=30
; speed_travel_mm_s=40
; virtual_filament_diameter_mm=1.75
; work_bounds=17,398,12,393,0,710
; machine_envelope=0,490,0,490,0,710
; stats.motion_count=45
; stats.print_motion_count=40
; stats.travel_motion_count=5
; stats.stroke_count=2
; stats.page_count=1
; stats.print_path_mm=280.944272
; stats.deposited_path_mm=270.944272
; stats.travel_path_mm=191.376102
; stats.total_motion_path_mm=472.320374
; stats.motion_time_seconds=14.149212
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=14.149212
; stats.body_volume_mm3=3131.622356
; stats.wet_weight_g=5.63692
; stats.body_e=1301.977281
; stats.pressure_e_excluded=0
; stats.warning_count=4
; nominal_label=calibrated centerline
; stats.warning_count.open_end=4
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
; parameter.stack_page_0_material_z_max_mm=4.0
; parameter.stack_page_0_material_z_min_mm=2.0
; parameter.stack_page_0_nominal_path_start_z_mm=2.0
; parameter.stack_page_0_nominal_top_z_mm=2.0
; parameter.stack_page_0_path_start_z_mm=2.0
; parameter.stack_page_0_z_max_mm=4.000000001
; parameter.stack_page_0_z_min_mm=2.0
; parameter.stack_page_material_height_mm=2.0
; parameter.stack_total_height_mm=4.0
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-01-crossing page_name=crossing z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X147.5 Y262.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start XY at safe Z
G0 X147.5 Y262.5 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0000 note=stroke start vertical approach
G1 X147.5 Y261 Z2 E0.514493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y259.5 Z2 E2.057971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y258 Z2 E4.630434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y256.5 Z2 E8.231883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y255 Z2 E12.862318 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y253.5 Z2 E18.521738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y252 Z2 E25.210143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y250.5 Z2 E32.927534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y249 Z2 E41.67391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y247.5 Z2 E51.449271 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X147.5 Y237.5 Z2 E120.0483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.5 Y222.5 Z2 E188.647328 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.5 Y222.5 Z2 E371.578071 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.5 Y187.082576 Z2 E533.551465 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.5 Y182.5 Z2 E564.987489 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.5 Y182.5 Z2 E613.006809 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X227.5 Y182.5 Z2 E763.924671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X227.5 Y142.5 Z2 E946.855414 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.5 Y142.5 Z2 E1084.053471 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.5 Y142.5 Z2 E1118.352985 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.5 Y142.5 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G0 X267.5 Y142.5 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0001 note=intra-page lift
G0 X189.5 Y162.5 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0001 note=intra-page XY
G0 X189.5 Y162.5 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X189.5 Y164 Z2 E1118.867478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y165.5 Z2 E1120.410956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y167 Z2 E1122.98342 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y168.5 Z2 E1126.584869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y170 Z2 E1131.215303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y171.5 Z2 E1136.874723 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y173 Z2 E1143.563128 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y174.5 Z2 E1151.280519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y176 Z2 E1160.026895 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y177.25 Z2 E1168.101573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X189.5 Y177.473607 Z2.111803 E1169.802257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2 matz1=2.111803 note=collision lift
G1 X189.5 Y177.5 Z2.125 E1170.004682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.111803 matz1=2.125 note=collision lift
G1 X189.5 Y181.25 Z4 E1198.765699 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.125 matz1=4 note=collision lift
G1 X189.5 Y183.75 Z4 E1215.915457 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=4 matz1=4 note=collision lift
G1 X189.5 Y187.5 Z2.125 E1244.676474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=4 matz1=2.125 note=collision lift
G1 X189.5 Y187.75 Z2 E1245.954741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.125 matz1=2 note=collision lift
G1 X189.5 Y192.5 Z2 E1267.677767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X189.5 Y197.5 Z2 E1301.977281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X189.5 Y202.5 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
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
