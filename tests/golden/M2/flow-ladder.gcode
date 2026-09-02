; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=calibration-flow-ladder
; prepared_trace_sha256=ec70b9de05815ee33d3584dc5594d03deb9149f3c2db3e2567ed225b6dfaf5fc
; body_sha256=cd484b82c4b140098e0424f7ff152f550dbd27dabb5daf5860b62487ccbe8bdc
; profile_name=potterbot-xl
; profile_version=1.3.0
; profile_verified=true
; profile_flavor=marlin
; extrusion_mode=absolute
; bead_width_mm=5
; layer_height_mm=1.5
; flow_multiplier=1
; wet_density_g_cm3=1.8
; prime_mm=15
; end_early_mm=5
; first_layer_z_mm=1.5
; speed_default_mm_s=40
; speed_first_layer_mm_s=30
; speed_travel_mm_s=40
; virtual_filament_diameter_mm=1.75
; work_bounds=17,398,12,393,0,710
; machine_envelope=0,490,0,490,0,710
; stats.motion_count=104
; stats.print_motion_count=84
; stats.travel_motion_count=20
; stats.stroke_count=7
; stats.page_count=1
; stats.print_path_mm=560
; stats.deposited_path_mm=525
; stats.travel_path_mm=152.5
; stats.total_motion_path_mm=712.5
; stats.motion_time_seconds=22.479167
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=22.479167
; stats.body_volume_mm3=3543.75
; stats.wet_weight_g=6.37875
; stats.body_e=1473.320045
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=calibration-flow-ladder calibration
; parameter.calibration=flow-ladder
; parameter.flow_values=0.70,0.80,0.90,1.00,1.10,1.20,1.30
; parameter.ladder_length_mm=80
; parameter.ladder_spacing_mm=10
; parameter.nozzle_diameter_mm=5
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
; CLAYLINE_MARKER page=0 layer=0 text=FLOW 0.70
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=flow-0.70
G0 X167.5 Y172.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=flow-0.70 note=stroke start XY at safe Z
G0 X167.5 Y172.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=flow-0.70 note=stroke start vertical approach
G1 X169 Y172.5 Z1.5 E0.163702 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X170.5 Y172.5 Z1.5 E0.654809 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X172 Y172.5 Z1.5 E1.47332 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X173.5 Y172.5 Z1.5 E2.619236 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X175 Y172.5 Z1.5 E4.092556 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X176.5 Y172.5 Z1.5 E5.89328 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X178 Y172.5 Z1.5 E8.021409 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X179.5 Y172.5 Z1.5 E10.476943 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X181 Y172.5 Z1.5 E13.25988 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X182.5 Y172.5 Z1.5 E16.370223 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=prime ramp
G1 X242.5 Y172.5 Z1.5 E147.332004 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70
G1 X247.5 Y172.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.70 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=flow-0.70
; CLAYLINE_MARKER page=0 layer=0 text=FLOW 0.80
G0 X247.5 Y172.5 Z3.5 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=none
G0 X247.5 Y182.5 Z3.5 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=none
G0 X247.5 Y182.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=none
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=flow-0.80
G1 X246 Y182.5 Z1.5 E147.519093 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X244.5 Y182.5 Z1.5 E148.080358 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X243 Y182.5 Z1.5 E149.015799 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X241.5 Y182.5 Z1.5 E150.325417 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X240 Y182.5 Z1.5 E152.009211 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X238.5 Y182.5 Z1.5 E154.067182 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X237 Y182.5 Z1.5 E156.499329 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X235.5 Y182.5 Z1.5 E159.305653 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X234 Y182.5 Z1.5 E162.486153 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X232.5 Y182.5 Z1.5 E166.04083 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=prime ramp
G1 X172.5 Y182.5 Z1.5 E315.711438 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80
G1 X167.5 Y182.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.80 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=flow-0.80
; CLAYLINE_MARKER page=0 layer=0 text=FLOW 0.90
G0 X167.5 Y182.5 Z3.5 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=none
G0 X167.5 Y192.5 Z3.5 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=none
G0 X167.5 Y192.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=none
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=flow-0.90
G1 X169 Y192.5 Z1.5 E315.921912 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X170.5 Y192.5 Z1.5 E316.553335 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X172 Y192.5 Z1.5 E317.605707 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X173.5 Y192.5 Z1.5 E319.079027 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X175 Y192.5 Z1.5 E320.973295 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X176.5 Y192.5 Z1.5 E323.288513 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X178 Y192.5 Z1.5 E326.024678 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X179.5 Y192.5 Z1.5 E329.181793 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X181 Y192.5 Z1.5 E332.759856 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X182.5 Y192.5 Z1.5 E336.758867 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=prime ramp
G1 X242.5 Y192.5 Z1.5 E505.138301 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90
G1 X247.5 Y192.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-0.90 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=flow-0.90
; CLAYLINE_MARKER page=0 layer=0 text=FLOW 1.00
G0 X247.5 Y192.5 Z3.5 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=none
G0 X247.5 Y202.5 Z3.5 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=none
G0 X247.5 Y202.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=none
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=flow-1.00
G1 X246 Y202.5 Z1.5 E505.372161 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X244.5 Y202.5 Z1.5 E506.073742 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X243 Y202.5 Z1.5 E507.243044 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X241.5 Y202.5 Z1.5 E508.880066 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X240 Y202.5 Z1.5 E510.984809 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X238.5 Y202.5 Z1.5 E513.557273 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X237 Y202.5 Z1.5 E516.597457 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X235.5 Y202.5 Z1.5 E520.105362 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X234 Y202.5 Z1.5 E524.080987 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X232.5 Y202.5 Z1.5 E528.524333 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=prime ramp
G1 X172.5 Y202.5 Z1.5 E715.612593 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00
G1 X167.5 Y202.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.00 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=flow-1.00
; CLAYLINE_MARKER page=0 layer=0 text=FLOW 1.10
G0 X167.5 Y202.5 Z3.5 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=none
G0 X167.5 Y212.5 Z3.5 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=none
G0 X167.5 Y212.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=none
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=flow-1.10
G1 X169 Y212.5 Z1.5 E715.869839 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X170.5 Y212.5 Z1.5 E716.641579 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X172 Y212.5 Z1.5 E717.92781 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X173.5 Y212.5 Z1.5 E719.728535 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X175 Y212.5 Z1.5 E722.043752 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X176.5 Y212.5 Z1.5 E724.873462 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X178 Y212.5 Z1.5 E728.217665 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X179.5 Y212.5 Z1.5 E732.07636 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X181 Y212.5 Z1.5 E736.449548 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X182.5 Y212.5 Z1.5 E741.337229 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=prime ramp
G1 X242.5 Y212.5 Z1.5 E947.134314 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10
G1 X247.5 Y212.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.10 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=flow-1.10
; CLAYLINE_MARKER page=0 layer=0 text=FLOW 1.20
G0 X247.5 Y212.5 Z3.5 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=none
G0 X247.5 Y222.5 Z3.5 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=none
G0 X247.5 Y222.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=none
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=flow-1.20
G1 X246 Y222.5 Z1.5 E947.414947 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X244.5 Y222.5 Z1.5 E948.256844 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X243 Y222.5 Z1.5 E949.660006 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X241.5 Y222.5 Z1.5 E951.624433 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X240 Y222.5 Z1.5 E954.150124 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X238.5 Y222.5 Z1.5 E957.23708 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X237 Y222.5 Z1.5 E960.885301 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X235.5 Y222.5 Z1.5 E965.094787 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X234 Y222.5 Z1.5 E969.865538 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X232.5 Y222.5 Z1.5 E975.197553 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=prime ramp
G1 X172.5 Y222.5 Z1.5 E1199.703465 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20
G1 X167.5 Y222.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.20 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=flow-1.20
; CLAYLINE_MARKER page=0 layer=0 text=FLOW 1.30
G0 X167.5 Y222.5 Z3.5 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=none
G0 X167.5 Y232.5 Z3.5 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=none
G0 X167.5 Y232.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=none
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=flow-1.30
G1 X169 Y232.5 Z1.5 E1200.007483 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X170.5 Y232.5 Z1.5 E1200.919539 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X172 Y232.5 Z1.5 E1202.439631 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X173.5 Y232.5 Z1.5 E1204.56776 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X175 Y232.5 Z1.5 E1207.303925 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X176.5 Y232.5 Z1.5 E1210.648128 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X178 Y232.5 Z1.5 E1214.600368 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X179.5 Y232.5 Z1.5 E1219.160644 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X181 Y232.5 Z1.5 E1224.328957 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X182.5 Y232.5 Z1.5 E1230.105307 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=prime ramp
G1 X242.5 Y232.5 Z1.5 E1473.320045 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30
G1 X247.5 Y232.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=flow-1.30 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=flow-1.30
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
