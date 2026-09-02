; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=calibrated
; prepared_trace_sha256=6633575a62897f1208377c3a5035dedf94da977b374f673867548d873837a898
; body_sha256=9fc03516f89d22666f3d1387eb2b0f1b1ceb0acb9659d365992ab7b9c35c570c
; profile_name=potterbot-xl
; profile_version=1.3.0
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
; stats.print_motion_count=37
; stats.travel_motion_count=8
; stats.stroke_count=3
; stats.page_count=1
; stats.print_path_mm=138.944272
; stats.deposited_path_mm=123.944272
; stats.travel_path_mm=135.813792
; stats.total_motion_path_mm=274.758064
; stats.motion_time_seconds=8.026821
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=8.026821
; stats.body_volume_mm3=865.388767
; stats.wet_weight_g=1.5577
; stats.body_e=359.786841
; stats.pressure_e_excluded=0
; stats.warning_count=6
; nominal_label=calibrated centerline
; stats.warning_count.open_end=6
; parameter.alternate=false
; parameter.collision_lift=bounded-clearance-v1
; parameter.first_layer_flow_factor=1.1
; parameter.first_layer_height=2.0
; parameter.first_layer_speed_factor=0.6
; parameter.flow_modulation=0.25
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.joint_boost=0.0
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-01-calibrated page_name=calibrated z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X263.5 Y232.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start XY at safe Z
G0 X263.5 Y232.5 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0000 note=stroke start vertical approach
G1 X262 Y232.5 Z2 E0.26052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X260.5 Y232.5 Z2 E1.042079 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X259 Y232.5 Z2 E2.344678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X257.5 Y232.5 Z2 E4.168316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X256.5 Y232.5 Z2 E5.673541 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X256 Y232.5 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X254.5 Y232.5 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X253 Y232.5 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X251.5 Y232.5 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G0 X251.5 Y232.5 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0001 note=intra-page lift
G0 X231.5 Y212.5 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0001 note=intra-page XY
G0 X231.5 Y212.5 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X230 Y212.5 Z2 E5.934061 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X228.5 Y212.5 Z2 E6.715621 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X227 Y212.5 Z2 E8.018219 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X225.5 Y212.5 Z2 E9.841858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X224 Y212.5 Z2 E12.186536 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X222.5 Y212.5 Z2 E15.052253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X221 Y212.5 Z2 E18.43901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X219.5 Y212.5 Z2 E22.346806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X218 Y212.5 Z2 E26.775642 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X216.5 Y212.5 Z2 E31.725518 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X156.5 Y212.5 Z2 E240.141327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X151.5 Y212.5 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
G0 X151.5 Y212.5 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0002 note=intra-page lift
G0 X159.5 Y218.5 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0002 note=intra-page XY
G0 X159.5 Y218.5 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0002
G1 X159.5 Y217.75 Z2 E240.206457 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X159.5 Y217.07918 Z2.33541 E240.401847 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=2 matz1=2.33541 note=collision lift
G1 X159.5 Y215.737539 Z3.006231 E241.183406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=2.33541 matz1=3.006231 note=collision lift
G1 X159.5 Y214.395898 Z3.677051 E242.486005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=3.006231 matz1=3.677051 note=collision lift
G1 X159.5 Y213.75 Z4 E243.298908 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=3.677051 matz1=4 note=collision lift
G1 X159.5 Y212.972136 Z4 E244.309643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=4 matz1=4 note=collision lift
G1 X159.5 Y211.472136 Z4 E246.654321 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=4 matz1=4 note=collision lift
G1 X159.5 Y211.25 Z4 E247.04584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=4 matz1=4 note=collision lift
G1 X159.5 Y210.107044 Z3.428522 E249.520038 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=4 matz1=3.428522 note=collision lift
G1 X159.5 Y208.765403 Z2.757701 E252.906795 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=3.428522 matz1=2.757701 note=collision lift
G1 X159.5 Y207.423762 Z2.086881 E256.814592 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=2.757701 matz1=2.086881 note=collision lift
G1 X159.5 Y207.25 Z2 E257.35882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 matz0=2.086881 matz1=2 note=collision lift
G1 X159.5 Y205.944272 Z2 E261.243428 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X159.5 Y204.444272 Z2 E266.193303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X159.5 Y177.5 Z2 E359.786841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X159.5 Y172.5 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0002
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
