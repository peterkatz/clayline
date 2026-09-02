; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=helical-page-01-golden-loop
; prepared_trace_sha256=7a58d1995c837252fb13fcbe98e36fe22a8a5845b2355d2a3bc2e33c581603f0
; body_sha256=c6f8f7e877618dfe7d8ab76645780fa2c6ce03cb04d28afd7227ea9e6f670ea2
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
; first_layer_z_mm=2.023673
; speed_default_mm_s=40
; speed_first_layer_mm_s=30
; speed_travel_mm_s=40
; virtual_filament_diameter_mm=1.75
; work_bounds=17,398,12,393,0,710
; machine_envelope=0,490,0,490,0,710
; stats.motion_count=102
; stats.print_motion_count=98
; stats.travel_motion_count=4
; stats.stroke_count=3
; stats.page_count=1
; stats.print_path_mm=380.162915
; stats.deposited_path_mm=365.162915
; stats.travel_path_mm=46.614825
; stats.total_motion_path_mm=426.77774
; stats.motion_time_seconds=11.725478
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=11.725478
; stats.body_volume_mm3=3540.853234
; stats.wet_weight_g=6.373536
; stats.body_e=1472.115709
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=calibrated centerline
; parameter.alternate=true
; parameter.first_layer_flow_factor=1.1
; parameter.first_layer_speed_factor=0.6
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=true
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
; parameter.z_modulation=0.0
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
G1 X188.999813 Y185 Z2.023673 E0.342995 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X190.499626 Y185 Z2.047347 E1.371981 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X191.99944 Y185 Z2.07102 E3.086956 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X193.499253 Y185 Z2.094694 E5.487922 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X194.999066 Y185 Z2.118367 E8.574879 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X196.498879 Y185 Z2.142041 E12.347825 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X197.998692 Y185 Z2.165714 E16.806762 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X199.498505 Y185 Z2.189388 E21.951689 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X200.998319 Y185 Z2.213061 E27.782607 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X202.498132 Y185 Z2.236735 E34.299514 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=prime ramp
G1 X212.5 Y185 Z2.394607 E80.046442 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X227.5 Y200 Z2.729442 E177.072203 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X212.5 Y220 Z3.12405 E291.418158 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X187.5 Y215 Z3.526471 E408.02861 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X187.5 Y189.999377 Z3.921088 E522.377415 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop
G1 X187.5 Y185 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=golden-loop note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=golden-loop
; CLAYLINE_MARKER page=0 layer=1 text=layer 1 page_id=golden-page page_name=golden-loop z_mode=calibrated
G0 X187.5 Y185 Z4.039461 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=golden-loop note=vertical layer transition
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=golden-loop
G1 X188.999813 Y185 Z4.063134 E522.689228 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.039461 matz1=4.063134 note=collision lift
G1 X190.499626 Y185 Z4.086808 E523.62467 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.063134 matz1=4.086808 note=collision lift
G1 X191.99944 Y185 Z4.110481 E525.183738 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.086808 matz1=4.110481 note=collision lift
G1 X193.499253 Y185 Z4.134155 E527.366435 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.110481 matz1=4.134155 note=collision lift
G1 X194.999066 Y185 Z4.157828 E530.172759 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.134155 matz1=4.157828 note=collision lift
G1 X196.498879 Y185 Z4.181502 E533.60271 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.157828 matz1=4.181502 note=collision lift
G1 X197.998692 Y185 Z4.205175 E537.656289 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.181502 matz1=4.205175 note=collision lift
G1 X199.498505 Y185 Z4.228849 E542.333496 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.205175 matz1=4.228849 note=collision lift
G1 X200.998319 Y185 Z4.252522 E547.63433 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.228849 matz1=4.252522 note=collision lift
G1 X202.498132 Y185 Z4.276196 E553.558791 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.252522 matz1=4.276196 note=collision lift
G1 X209.992528 Y185 Z4.394489 E584.720751 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.276196 matz1=4.394489 note=collision lift
G1 X210 Y185 Z4.398343 E584.755705 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.394489 matz1=4.398343 note=collision lift
G1 X212.5 Y185 Z4.436792 E595.150726 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.398343 matz1=4.436792 note=collision lift
G1 X212.503853 Y185.003853 Z4.436792 E595.173381 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.436792 matz1=4.436792 note=collision lift
G1 X225.724211 Y198.224211 Z4.729263 E672.913526 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.436792 matz1=4.729263 note=collision lift
G1 X225.732233 Y198.232233 Z4.735115 E672.9666 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.729263 matz1=4.735115 note=collision lift
G1 X226.174175 Y198.674175 Z4.75344 E675.566165 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.735115 matz1=4.75344 note=collision lift
G1 X226.175632 Y198.675632 Z4.75344 E675.57473 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.75344 matz1=4.75344 note=collision lift
G1 X226.614858 Y199.114858 Z4.761473 E678.15743 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.75344 matz1=4.761473 note=collision lift
G1 X226.616117 Y199.116117 Z4.762391 E678.165755 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.761473 matz1=4.762391 note=collision lift
G1 X227.5 Y200 Z4.77017 E683.362752 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.762391 matz1=4.77017 note=collision lift
G1 X227.49848 Y200.002027 Z4.77017 E683.373287 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.77017 matz1=4.77017 note=collision lift
G1 X214.011036 Y217.985285 Z5.123759 E776.84197 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=4.77017 matz1=5.123759 note=collision lift
G1 X214 Y218 Z5.133246 E776.928016 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.123759 matz1=5.133246 note=collision lift
G1 X212.5 Y220 Z5.168264 E787.322827 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.133246 matz1=5.168264 note=collision lift
G1 X212.490678 Y219.998136 Z5.168264 E787.362353 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.168264 matz1=5.168264 note=collision lift
G1 X189.968122 Y215.493624 Z5.526203 E882.86625 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.168264 matz1=5.526203 note=collision lift
G1 X189.951452 Y215.49029 Z5.534972 E882.945776 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.526203 matz1=5.534972 note=collision lift
G1 X188.725726 Y215.245145 Z5.55984 E888.143701 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.534972 matz1=5.55984 note=collision lift
G1 X188.722877 Y215.244575 Z5.55984 E888.15578 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.55984 matz1=5.55984 note=collision lift
G1 X187.5 Y215 Z5.567174 E893.340686 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.55984 matz1=5.567174 note=collision lift
G1 X187.5 Y214.997516 Z5.567174 E893.351014 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.567174 matz1=5.567174 note=collision lift
G1 X187.5 Y189.99969 Z5.960654 E997.29277 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.567174 matz1=5.960654 note=collision lift
G1 X187.5 Y187.5 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=5.960654 matz1=6 note=collision lift
G1 X187.5 Y185 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=golden-loop matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=golden-loop
; CLAYLINE_MARKER page=0 layer=2 text=layer 2 page_id=golden-page page_name=golden-loop z_mode=calibrated
G0 X187.5 Y185 Z8 F2400 ; clayline kind=travel_approach page=0 layer=2 stroke=golden-loop note=vertical layer transition
; CLAYLINE_STROKE_BEGIN page=0 layer=2 id=golden-loop
G1 X189 Y185 Z8 E997.604584 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X190.5 Y185 Z8 E998.540025 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X191.342157 Y185 Z8 E999.338569 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X192 Y185 Z8 E1000.099094 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X193.5 Y185 Z8 E1002.28179 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X195 Y185 Z8 E1005.088114 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X196.5 Y185 Z8 E1008.518065 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X198 Y185 Z8 E1012.571644 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X199.5 Y185 Z8 E1017.248851 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X201 Y185 Z8 E1022.549685 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X202.5 Y185 Z8 E1028.474147 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X207.492528 Y185 Z8 E1049.230666 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X207.5 Y185 Z8 E1049.261731 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X209.99661 Y185 Z8 E1059.641429 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X210.003856 Y185 Z8 E1059.671555 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X212.5 Y185 Z8 E1070.049315 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X212.503807 Y185.003807 Z8 E1070.071697 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X223.956444 Y196.456444 Z8 E1137.408813 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X223.964466 Y196.464466 Z8 E1137.455982 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X224.406408 Y196.906408 Z8 E1140.05443 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X224.407865 Y196.907865 Z8 E1140.062996 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X224.847091 Y197.347091 Z8 E1142.645479 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X224.84835 Y197.34835 Z8 E1142.652878 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X225.718661 Y198.218661 Z8 E1147.769979 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X225.732487 Y198.232487 Z8 E1147.85127 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X226.616244 Y199.116244 Z8 E1153.047418 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X226.618425 Y199.118425 Z8 E1153.060245 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X227.5 Y200 Z8 E1158.243567 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X227.498485 Y200.00202 Z8 E1158.254063 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X215.511036 Y215.985285 Z8 E1241.317432 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X215.5 Y216 Z8 E1241.393904 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X214.008231 Y217.989025 Z8 E1251.730659 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X213.99753 Y218.003293 Z8 E1251.804811 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X212.5 Y220 Z8 E1262.181489 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X212.490828 Y219.998166 Z8 E1262.220375 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X192.419574 Y215.983915 Z8 E1347.319524 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X192.402903 Y215.980581 Z8 E1347.390203 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X191.177178 Y215.735436 Z8 E1352.587099 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X191.174329 Y215.734866 Z8 E1352.599178 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X189.96722 Y215.493444 Z8 E1357.717138 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X189.950973 Y215.490195 Z8 E1357.786025 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X188.725486 Y215.245097 Z8 E1362.981906 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X188.722649 Y215.24453 Z8 E1362.993937 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X187.5 Y215 Z8 E1368.177787 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X187.5 Y214.997524 Z8 E1368.188082 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X187.5 Y190 Z8 E1472.115709 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
G1 X187.5 Y185 Z8 F2400 ; clayline kind=print page=0 layer=2 stroke=golden-loop matz0=8 matz1=8 note=collision lift
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
