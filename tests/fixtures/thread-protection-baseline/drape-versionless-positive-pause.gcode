; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=drape-a-job
; prepared_trace_sha256=7596039a26cf820ffa868d70acae34ae2423982a1d878300df92eb10367570fe
; body_sha256=c4bf96d66492295e90ecb2f9d57be6a8eea1cb3fe14c2b436503796956a90402
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
; stats.stroke_count=4
; stats.page_count=2
; stats.print_path_mm=544.72136
; stats.deposited_path_mm=522.72136
; stats.travel_path_mm=102.111026
; stats.total_motion_path_mm=646.832385
; stats.motion_time_seconds=23.517748
; stats.pause_time_seconds=3
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=26.517748
; stats.body_volume_mm3=7177.220053
; stats.wet_weight_g=12.918996
; stats.body_e=2983.941353
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
; parameter.joint_boost=0.5
; parameter.layers=1
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_mode=stack
; parameter.page_pause_seconds=3.0
; parameter.page_travel_clearance=50.0
; parameter.page_travel_lift=4.0
; parameter.provisional_flow_multiplier=1.0
; parameter.stack_job_page_count=2
; parameter.stack_page_0_path_start_z_mm=20.0
; parameter.stack_page_0_z_max_mm=20.0
; parameter.stack_page_0_z_min_mm=20.0
; parameter.stack_page_1_path_start_z_mm=22.0
; parameter.stack_page_1_prior_top_mm=2.0
; parameter.stack_page_1_z_max_mm=22.0
; parameter.stack_page_1_z_min_mm=22.0
; parameter.stack_page_material_height_mm=2.0
; parameter.stack_total_height_mm=4.0
; parameter.standoff_z=20.0
; parameter.z_mode=drape
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
G0 X147.5 Y242.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=thread launch position
G1 E146.938776 F2400 ; clayline kind=thread_launch page=0 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-01-drape-a page_name=drape-a z_mode=drape
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G1 X157.5 Y242.5 Z20 E220.408163 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.5 Y242.5 Z20 E612.244898 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.5 Y202.5 Z20 E808.163265 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.5 Y192.5 Z20 E881.632653 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G1 X247.5 Y172.5 Z20 E991.15435 F2400 ; clayline kind=carry page=0 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X237.5 Y172.5 Z20 E1064.623738 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X167.5 Y172.5 Z20 E1407.480881 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X157.5 Y172.5 Z20 E1480.950268 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X158.5 Y172.5 Z20 E1483.15435 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X159.5 Y172.5 Z20 E1485.113534 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X160.5 Y172.5 Z20 E1486.827819 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X161.5 Y172.5 Z20 E1488.297207 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X162.5 Y172.5 Z20 E1489.521697 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X163.5 Y172.5 Z20 E1490.501289 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X164.5 Y172.5 Z20 E1491.235983 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X165.5 Y172.5 Z20 E1491.725778 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X166.5 Y172.5 Z20 E1491.970676 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X167.5 Y172.5 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X177.5 Y172.5 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=1
G0 X177.5 Y172.5 Z26 F2400 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0001 note=inter-page clearance above completed material
G0 X157.5 Y172.5 Z26 F2400 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0001 note=inter-page XY within common stack footprint
G4 S3
G0 X157.5 Y172.5 Z22 F2400 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0001 note=inter-page approach
G1 E1638.909452 F2400 ; clayline kind=thread_launch page=1 layer=0 stroke=stroke-0001 note=thread launch
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-drape-b page_name=drape-b z_mode=drape
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X167.5 Y172.5 Z22 E1712.37884 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.5 Y172.5 Z22 E2055.235983 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X247.5 Y172.5 Z22 E2128.70537 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
G1 X237.5 Y192.5 Z22 E2238.227067 F2400 ; clayline kind=carry page=1 layer=0 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z22 E2311.696455 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X237.5 Y242.5 Z22 E2507.614822 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.5 Y242.5 Z22 E2899.451557 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.5 Y242.5 Z22 E2972.920945 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X148.413812 Y242.093862 Z22 E2975.125026 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X149.327623 Y241.687723 Z22 E2977.08421 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X150.241435 Y241.281585 Z22 E2978.798496 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X151.155246 Y240.875446 Z22 E2980.267884 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X152.069058 Y240.469308 Z22 E2981.492373 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X152.982869 Y240.063169 Z22 E2982.471965 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X153.896681 Y239.657031 Z22 E2983.206659 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X154.810492 Y239.250892 Z22 E2983.696455 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X155.724304 Y238.844754 Z22 E2983.941353 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X156.638115 Y238.438615 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
G1 X165.776231 Y234.377231 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000 note=thread landing
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
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
