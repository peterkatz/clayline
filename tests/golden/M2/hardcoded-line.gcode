; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=m2-hardcoded-line
; prepared_trace_sha256=edb744103e528e9f85362f1e05579131717d218fd3a510c53af069f2eba9d2f6
; body_sha256=f05b8eabbb1e93d5df92cf1a8903789690bf614f6354d3158fa8306a5141539b
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
; stats.motion_count=14
; stats.print_motion_count=12
; stats.travel_motion_count=2
; stats.stroke_count=1
; stats.page_count=1
; stats.print_path_mm=40
; stats.deposited_path_mm=35
; stats.travel_path_mm=167.034508
; stats.total_motion_path_mm=207.034508
; stats.motion_time_seconds=5.175863
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=5.175863
; stats.body_volume_mm3=206.25
; stats.wet_weight_g=0.37125
; stats.body_e=85.748786
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=calibrated line
; parameter.pattern=hardcoded-line
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
; CLAYLINE_MARKER page=0 layer=0 text=M2 deterministic line
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=line-1
G0 X100 Y100 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=line-1 note=stroke start XY at safe Z
G0 X100 Y100 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=line-1 note=stroke start vertical approach
G1 X101.5 Y100 Z1.5 E0.23386 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X103 Y100 Z1.5 E0.935441 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X104.5 Y100 Z1.5 E2.104743 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X106 Y100 Z1.5 E3.741765 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X107.5 Y100 Z1.5 E5.846508 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X109 Y100 Z1.5 E8.418972 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X110.5 Y100 Z1.5 E11.459156 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X112 Y100 Z1.5 E14.967061 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X113.5 Y100 Z1.5 E18.942686 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X115 Y100 Z1.5 E23.386032 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=prime ramp
G1 X135 Y100 Z1.5 E85.748786 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1
G1 X140 Y100 Z1.5 F2400 ; clayline kind=print page=0 layer=0 stroke=line-1 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=line-1
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
