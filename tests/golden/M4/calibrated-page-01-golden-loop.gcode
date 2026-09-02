; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=calibrated-page-01-golden-loop
; prepared_trace_sha256=83861a08e6faed4b470d5e7093016b119ebe3f276d32d3efa21bf5985239b6ff
; body_sha256=dc25185409e289195bcdfd5a5c2f625f1986d9e5a860fd76cb3218767a9e702b
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
; first_layer_z_mm=1.978572
; speed_default_mm_s=40
; speed_first_layer_mm_s=30
; speed_travel_mm_s=40
; virtual_filament_diameter_mm=1.75
; work_bounds=17,398,12,393,0,710
; machine_envelope=0,490,0,490,0,710
; stats.motion_count=79
; stats.print_motion_count=75
; stats.travel_motion_count=4
; stats.stroke_count=3
; stats.page_count=1
; stats.print_path_mm=381.248378
; stats.deposited_path_mm=366.248378
; stats.travel_path_mm=48.023101
; stats.total_motion_path_mm=429.271479
; stats.motion_time_seconds=11.787908
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=11.787908
; stats.body_volume_mm3=3553.655221
; stats.wet_weight_g=6.396579
; stats.body_e=1477.438157
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=calibrated centerline
; parameter.alternate=true
; parameter.first_layer_flow_factor=1.1
; parameter.first_layer_speed_factor=0.6
; parameter.flow_modulation=0.15
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
; parameter.standoff_z=20.0
; parameter.z_mode=calibrated
; parameter.z_modulation=0.4
; parameter.z_step_per_layer=2
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=golden-page page_name=golden-loop z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=golden-loop
G0 X187.5 Y185 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=golden-loop note=stroke start XY at safe Z
G0 X187.5 Y185 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=golden-loop note=stroke start vertical approach
G1 X188.999847 Y185 Z1.978572 E0.297055 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X190.499694 Y185 Z1.957144 E1.188219 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X191.999541 Y185 Z1.935716 E2.673493 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X193.499388 Y185 Z1.914288 E4.752876 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X194.999235 Y185 Z1.89286 E7.426369 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X196.499082 Y185 Z1.871432 E10.693971 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X197.998929 Y185 Z1.850004 E14.555683 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X199.498776 Y185 Z1.828576 E19.011505 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X200.998622 Y185 Z1.807148 E24.061435 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X202.498469 Y185 Z1.78572 E29.705476 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X212.5 Y185 Z1.64283 E69.322882 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X227.5 Y200 Z2.399992 E180.95937 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X212.5 Y220 Z1.81769 E287.503552 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X187.5 Y215 Z1.737863 E392.638454 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X187.5 Y189.999451 Z2.10849 E514.815403 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X187.5 Y185 Z2.182606 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=golden-loop
; CLAYLINE_MARKER page=0 layer=1 text=layer 1 page_id=golden-page page_name=golden-loop z_mode=calibrated
G0 X187.5 Y185 Z4.34641 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=golden-loop note=vertical layer transition
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=golden-loop
G1 X187.5 Y186.499999 Z4.344827 E515.164019 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y187.999998 Z4.343243 E516.209868 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y189.499997 Z4.34166 E517.952949 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y190.999997 Z4.340076 E520.393263 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y192.499996 Z4.338492 E523.530809 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y193.999995 Z4.336909 E527.365588 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y195.499994 Z4.335325 E531.8976 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y196.999993 Z4.333742 E537.126844 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y198.499992 Z4.332158 E543.05332 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y199.999992 Z4.330575 E549.677029 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop note=prime ramp
G1 X187.5 Y215 Z4.314739 E619.400358 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop
G1 X210.037298 Y219.50746 Z3.817938 E702.555689 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.314739 matz1=3.817938 note=collision lift
G1 X210.048548 Y219.50971 Z3.823377 E702.601616 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=3.817938 matz1=3.823377 note=collision lift
G1 X211.274274 Y219.754855 Z3.860073 E707.125039 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=3.823377 matz1=3.860073 note=collision lift
G1 X211.27655 Y219.75531 Z3.858853 E707.134525 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=3.860073 matz1=3.858853 note=collision lift
G1 X212.5 Y220 Z3.87746 E711.648107 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=3.858853 matz1=3.87746 note=collision lift
G1 X212.501811 Y219.997586 Z3.875991 E711.661945 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=3.87746 matz1=3.875991 note=collision lift
G1 X226 Y202 Z4.399992 E804.436613 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=3.875991 matz1=4.399992 note=collision lift
G1 X227.5 Y200 Z4.399992 E814.743497 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.399992 matz1=4.399992 note=collision lift
G1 X225.732233 Y198.232233 Z4.399992 E825.907243 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.399992 matz1=4.399992 note=collision lift
G1 X212.5 Y185 Z4.197542 E909.475915 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.399992 matz1=4.197542 note=collision lift
G1 X193.611614 Y185 Z4.031709 E976.242397 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.197542 matz1=4.031709 note=collision lift
G1 X192.135822 Y185 Z4.734359 E982.019884 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.031709 matz1=4.51699 note=collision lift
G1 X188.75 Y185 Z6.34641 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.51699 matz1=5.630343 note=collision lift
G1 X187.5 Y185 Z6.34641 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.630343 matz1=5.60049 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=golden-loop
; CLAYLINE_MARKER page=0 layer=2 text=layer 2 page_id=golden-page page_name=golden-loop z_mode=calibrated
G0 X187.5 Y185 Z7.630343 F2400 ; clayline kind=travel_approach page=0 layer=2 stroke=golden-loop note=vertical layer transition
; CLAYLINE_STROKE_BEGIN page=0 layer=2 id=golden-loop
G1 X189 Y185 Z7.630343 E982.370816 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.630343 matz1=7.630343 note=collision lift
G1 X190.5 Y185 Z7.630343 E983.423611 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.630343 matz1=7.630343 note=collision lift
G1 X191.25 Y185 Z7.630343 E984.213207 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.630343 matz1=7.630343 note=collision lift
G1 X191.96247 Y185 Z7.396063 E985.178269 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.630343 matz1=7.396063 note=collision lift
G1 X193.387409 Y185 Z6.927503 E987.63479 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.396063 matz1=6.927503 note=collision lift
G1 X194.812348 Y185 Z6.458944 E990.793175 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.927503 matz1=6.458944 note=collision lift
G1 X195.952435 Y185 Z6.084051 E993.825611 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.458944 matz1=6.084051 note=collision lift
G1 X196.252267 Y185 Z6.087944 E994.653423 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.084051 matz1=6.087944 note=collision lift
G1 X197.752141 Y185 Z6.107419 E999.215534 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.087944 matz1=6.107419 note=collision lift
G1 X199.252014 Y185 Z6.126893 E1004.479508 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.107419 matz1=6.126893 note=collision lift
G1 X200.751888 Y185 Z6.146367 E1010.445346 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.126893 matz1=6.146367 note=collision lift
G1 X202.251761 Y185 Z6.165842 E1017.113046 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.146367 matz1=6.165842 note=collision lift
G1 X210 Y185 Z6.266445 E1053.370795 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.165842 matz1=6.266445 note=collision lift
G1 X212.5 Y185 Z6.33454 E1065.072854 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop
G1 X223.964466 Y196.464466 Z6.399992 E1127.369913 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.33454 matz1=6.399992 note=collision lift
G1 X227.5 Y200 Z6.399992 E1146.581585 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.399992 matz1=6.399992 note=collision lift
G1 X224.5 Y204 Z6.399992 E1165.676152 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.399992 matz1=6.399992 note=collision lift
G1 X212.501766 Y219.997646 Z5.934219 E1242.063893 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.399992 matz1=5.934219 note=collision lift
G1 X212.5 Y220 Z5.935689 E1242.076456 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=5.934219 matz1=5.935689 note=collision lift
G1 X211.277191 Y219.755438 Z5.917094 E1248.025179 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=5.935689 matz1=5.917094 note=collision lift
G1 X211.274913 Y219.754983 Z5.918311 E1248.037686 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=5.917094 matz1=5.918311 note=collision lift
G1 X210.049826 Y219.509965 Z5.881657 E1253.999391 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=5.918311 matz1=5.881657 note=collision lift
G1 X210.04112 Y219.508224 Z5.87743 E1254.046296 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=5.881657 matz1=5.87743 note=collision lift
G1 X209.836102 Y219.46722 Z5.876594 E1255.043565 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=5.87743 matz1=5.876594 note=collision lift
G1 X189.951452 Y215.49029 Z6.332917 E1351.792158 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=5.876594 matz1=6.332917 note=collision lift
G1 X187.5 Y215 Z6.392723 E1363.720068 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop
G1 X187.5 Y190.045003 Z6.350696 E1475.910014 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.392723 matz1=6.350696 note=collision lift
G1 X187.5 Y189.740264 Z6.50128 E1477.438157 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.350696 matz1=6.50128 note=collision lift
G1 X187.5 Y187.5 Z7.608282 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=6.50128 matz1=7.608282 note=collision lift
G1 X187.5 Y187.332532 Z7.623344 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.608282 matz1=7.623344 note=collision lift
G1 X187.5 Y187.330933 Z7.622536 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.623344 matz1=7.622536 note=collision lift
G1 X187.5 Y187.165064 Z7.630692 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.622536 matz1=7.630692 note=collision lift
G1 X187.5 Y187.164374 Z7.630343 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.630692 matz1=7.630343 note=collision lift
G1 X187.5 Y185 Z7.630343 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=7.630343 matz1=7.630343 note=collision lift
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
