; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=pages-job-page-01-rings-grid
; prepared_trace_sha256=5ca7ebb5394c2f0bfaff68ef4ea45dd4012a27862275c376ee62e56360eec079
; body_sha256=cfb6e577ed665227287f38b637f5aecaa865847b7c229019e520198d3b08d098
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
; stats.motion_count=2989
; stats.print_motion_count=2866
; stats.travel_motion_count=123
; stats.stroke_count=42
; stats.page_count=1
; stats.print_path_mm=4599.501096
; stats.deposited_path_mm=4389.501096
; stats.travel_path_mm=1396.050229
; stats.total_motion_path_mm=5995.551325
; stats.motion_time_seconds=169.053371
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=169.053371
; stats.body_volume_mm3=42782.261509
; stats.wet_weight_g=77.008071
; stats.body_e=17786.797442
; stats.pressure_e_excluded=0
; stats.warning_count=55
; nominal_label=calibrated centerline
; stats.warning_count.tight_radius=9
; stats.warning_count.under_spaced=46
; parameter.alternate=true
; parameter.first_layer_flow_factor=1.1
; parameter.first_layer_speed_factor=0.6
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.joint_boost=0.0
; parameter.layers=2
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_pause_seconds=disabled
; parameter.page_travel_clearance=50
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-0-rings-grid-1 page_name=rings-grid z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X46.010281 Y221.353281 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start XY at safe Z
G0 X46.010281 Y221.353281 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0000 note=stroke start vertical approach
G1 X45.002942 Y222.464707 Z2 E0.342995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X44.714614 Y222.782828 Z2 E0.567445 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X44.076824 Y223.642789 Z2 E1.371981 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X43.565307 Y224.332489 Z2 E2.269778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X43.235604 Y224.882566 Z2 E3.086956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X42.573428 Y225.98734 Z2 E5.107001 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X42.482796 Y226.178965 Z2 E5.487922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X41.841463 Y227.534949 Z2 E8.574879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X41.748528 Y227.731444 Z2 E9.079113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X41.316421 Y228.939102 Z2 E12.347825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X41.098553 Y229.548003 Z2 E14.186113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X40.891219 Y230.375726 Z2 E16.806762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X40.629761 Y231.419524 Z2 E20.428003 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X40.567554 Y231.83889 Z2 E21.951689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X40.347459 Y233.322655 Z2 E27.782607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X40.346668 Y233.327983 Z2 E27.804782 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X40.273331 Y234.820796 Z2 E34.299514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X40.252 Y235.255 Z2 E36.287641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X40.346668 Y237.182017 Z2 E45.111035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X40.629761 Y239.090476 Z2 E53.934429 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X41.098553 Y240.961997 Z2 E62.757824 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X41.748528 Y242.778556 Z2 E71.581218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X42.573428 Y244.52266 Z2 E80.404612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X43.565307 Y246.177511 Z2 E89.228007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X44.714614 Y247.727172 Z2 E98.051401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X46.010281 Y249.156719 Z2 E106.874795 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X47.439828 Y250.452386 Z2 E115.69819 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X48.989489 Y251.601693 Z2 E124.521584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X50.64434 Y252.593572 Z2 E133.344978 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X52.388444 Y253.418472 Z2 E142.168373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X54.205003 Y254.068447 Z2 E150.991767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X56.076524 Y254.537239 Z2 E159.815161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X57.984983 Y254.820332 Z2 E168.638556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X59.912 Y254.915 Z2 E177.46195 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X61.839017 Y254.820332 Z2 E186.285344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X63.747476 Y254.537239 Z2 E195.108739 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X65.618997 Y254.068447 Z2 E203.932133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X67.435556 Y253.418472 Z2 E212.755527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X69.17966 Y252.593572 Z2 E221.578922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X70.834511 Y251.601693 Z2 E230.402316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X72.384172 Y250.452386 Z2 E239.22571 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X73.813719 Y249.156719 Z2 E248.049105 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X75.109386 Y247.727172 Z2 E256.872499 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X76.258693 Y246.177511 Z2 E265.695893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X77.250572 Y244.52266 Z2 E274.519288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X78.075472 Y242.778556 Z2 E283.342682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X78.725447 Y240.961997 Z2 E292.166077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X79.194239 Y239.090476 Z2 E300.989471 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X79.477332 Y237.182017 Z2 E309.812865 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X79.572 Y235.255 Z2 E318.63626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X79.477332 Y233.327983 Z2 E327.459654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X79.194239 Y231.419524 Z2 E336.283048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X78.725447 Y229.548003 Z2 E345.106443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X78.075472 Y227.731444 Z2 E353.929837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X77.250572 Y225.98734 Z2 E362.753231 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X76.258693 Y224.332489 Z2 E371.576626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X75.109386 Y222.782828 Z2 E380.40002 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X73.813719 Y221.353281 Z2 E389.223414 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X72.384172 Y220.057614 Z2 E398.046809 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X70.834511 Y218.908307 Z2 E406.870203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X69.17966 Y217.916428 Z2 E415.693597 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X67.435556 Y217.091528 Z2 E424.516992 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X65.618997 Y216.441553 Z2 E433.340386 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X63.747476 Y215.972761 Z2 E442.16378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X61.839017 Y215.689668 Z2 E450.987175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X59.912 Y215.595 Z2 E459.810569 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X57.984983 Y215.689668 Z2 E468.633963 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X56.076524 Y215.972761 Z2 E477.457358 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X54.205003 Y216.441553 Z2 E486.280752 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X52.388444 Y217.091528 Z2 E495.104146 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X50.64434 Y217.916428 Z2 E503.927541 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X49.96843 Y218.321553 Z2 E507.531381 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X48.989489 Y218.908307 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X47.439828 Y220.057614 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X46.010281 Y221.353281 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G0 X46.010281 Y221.353281 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0001 note=intra-page lift
G0 X79.170621 Y229.659514 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0001 note=intra-page XY
G0 X79.170621 Y229.659514 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X78.806151 Y231.11456 Z2 E507.874376 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.729761 Y231.419524 Z2 E508.03322 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.555796 Y232.592306 Z2 E508.903362 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.446668 Y233.327983 Z2 E509.667934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.40956 Y234.083346 Z2 E510.618337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.352 Y235.255 Z2 E512.437537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.368042 Y235.581539 Z2 E513.019303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.441643 Y237.079732 Z2 E516.10626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.446668 Y237.182017 Z2 E516.342029 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.651738 Y238.564482 Z2 E519.879206 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.729761 Y239.090476 Z2 E521.38141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X78.965027 Y240.029709 Z2 E524.338143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X79.198553 Y240.961997 Z2 E527.55568 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X79.380106 Y241.469404 Z2 E529.48307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X79.848528 Y242.778556 Z2 E534.864839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X79.895375 Y242.877605 Z2 E535.313988 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X80.536708 Y244.233589 Z2 E541.830895 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X80.673428 Y244.52266 Z2 E543.2933 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X81.665307 Y246.177511 Z2 E552.116694 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X82.814614 Y247.727172 Z2 E560.940088 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X84.110281 Y249.156719 Z2 E569.763483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X85.539828 Y250.452386 Z2 E578.586877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X87.089489 Y251.601693 Z2 E587.410271 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X88.74434 Y252.593572 Z2 E596.233666 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X90.488444 Y253.418472 Z2 E605.05706 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X92.305003 Y254.068447 Z2 E613.880454 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X94.176524 Y254.537239 Z2 E622.703849 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X96.084983 Y254.820332 Z2 E631.527243 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X98.012 Y254.915 Z2 E640.350638 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X99.939017 Y254.820332 Z2 E649.174032 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X101.847476 Y254.537239 Z2 E657.997426 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X103.718997 Y254.068447 Z2 E666.820821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X105.535556 Y253.418472 Z2 E675.644215 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X107.27966 Y252.593572 Z2 E684.467609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X108.934511 Y251.601693 Z2 E693.291004 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X110.484172 Y250.452386 Z2 E702.114398 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X111.913719 Y249.156719 Z2 E710.937792 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X113.209386 Y247.727172 Z2 E719.761187 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X114.358693 Y246.177511 Z2 E728.584581 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X115.350572 Y244.52266 Z2 E737.407975 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X116.175472 Y242.778556 Z2 E746.23137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X116.825447 Y240.961997 Z2 E755.054764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X117.294239 Y239.090476 Z2 E763.878158 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X117.577332 Y237.182017 Z2 E772.701553 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X117.672 Y235.255 Z2 E781.524947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X117.577332 Y233.327983 Z2 E790.348341 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X117.294239 Y231.419524 Z2 E799.171736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X116.825447 Y229.548003 Z2 E807.99513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X116.175472 Y227.731444 Z2 E816.818524 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X115.350572 Y225.98734 Z2 E825.641919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X114.358693 Y224.332489 Z2 E834.465313 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X113.209386 Y222.782828 Z2 E843.288707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X111.913719 Y221.353281 Z2 E852.112102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X110.484172 Y220.057614 Z2 E860.935496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X108.934511 Y218.908307 Z2 E869.758891 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X107.27966 Y217.916428 Z2 E878.582285 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X105.535556 Y217.091528 Z2 E887.405679 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X103.718997 Y216.441553 Z2 E896.229074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X101.847476 Y215.972761 Z2 E905.052468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X99.939017 Y215.689668 Z2 E913.875862 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X98.012 Y215.595 Z2 E922.699257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X96.084983 Y215.689668 Z2 E931.522651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X94.176524 Y215.972761 Z2 E940.346045 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X92.305003 Y216.441553 Z2 E949.16944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X90.488444 Y217.091528 Z2 E957.992834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X88.74434 Y217.916428 Z2 E966.816228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X87.089489 Y218.908307 Z2 E975.639623 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X85.539828 Y220.057614 Z2 E984.463017 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X84.110281 Y221.353281 Z2 E993.286411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X82.814614 Y222.782828 Z2 E1002.109806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X81.665307 Y224.332489 Z2 E1010.9332 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X81.201084 Y225.106999 Z2 E1015.062762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X80.673428 Y225.98734 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
G1 X79.848528 Y227.731444 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
G1 X79.198553 Y229.548003 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
G1 X79.170621 Y229.659514 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
G0 X79.170621 Y229.659514 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0002 note=intra-page lift
G0 X79.178707 Y246.903413 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0002 note=intra-page XY
G0 X79.178707 Y246.903413 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0002
G1 X78.722939 Y246.903627 Z2 E1015.094428 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X77.811838 Y247.035824 Z2 E1015.351565 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X77.693272 Y247.070702 Z2 E1015.405757 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X76.950797 Y247.289109 Z2 E1015.851006 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X76.287964 Y247.585466 Z2 E1016.434743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X76.137305 Y247.652826 Z2 E1016.589842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X75.36885 Y248.116318 Z2 E1017.578586 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X75.033545 Y248.397434 Z2 E1018.149718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X73.957 Y249.3 Z2 E1020.377987 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X73.895862 Y249.372923 Z2 E1020.550684 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X72.932159 Y250.52239 Z2 E1023.637641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X72.773318 Y250.71185 Z2 E1024.212295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X72.309826 Y251.480305 Z2 E1026.454763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X72.164783 Y251.804709 Z2 E1027.410587 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.946109 Y252.293797 Z2 E1028.924412 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.692824 Y253.154838 Z2 E1031.656577 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.683242 Y253.220877 Z2 E1031.869524 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.560627 Y254.065939 Z2 E1034.714295 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.560324 Y254.712028 Z2 E1037.014451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.560175 Y255.029615 Z2 E1038.191753 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.702125 Y256.048375 Z2 E1042.215896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.742782 Y256.196716 Z2 E1042.845369 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X71.997134 Y257.124733 Z2 E1046.947052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X72.198415 Y257.6234 Z2 E1049.362276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X72.455857 Y258.261201 Z2 E1052.507764 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X73.088953 Y259.460291 Z2 E1058.708933 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X73.907078 Y260.724516 Z2 E1065.595601 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X74.920888 Y262.056386 Z2 E1073.250454 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X76.141041 Y263.458416 Z2 E1081.750411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X77.578193 Y264.933116 Z2 E1091.167509 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X79.243 Y266.483 Z2 E1101.569783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X80.610398 Y268.166771 Z2 E1111.489523 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X82.8245 Y270.460797 Z2 E1126.070146 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X85.840914 Y273.181268 Z2 E1144.64669 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X89.61525 Y276.144375 Z2 E1166.591527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X91.772767 Y277.659477 Z2 E1178.648325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X94.103117 Y279.166311 Z2 E1191.339521 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X96.600753 Y280.641899 Z2 E1204.606371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X99.260125 Y282.063266 Z2 E1218.396534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X102.075685 Y283.407435 Z2 E1232.664962 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X105.041883 Y284.651432 Z2 E1247.374871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X108.153171 Y285.772279 Z2 E1262.498782 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X111.404 Y286.747 Z2 E1278.019604 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X110.429279 Y283.496171 Z2 E1293.540426 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X109.308432 Y280.384883 Z2 E1308.664337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X108.064435 Y277.418685 Z2 E1323.374246 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X106.720266 Y274.603125 Z2 E1337.642674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X105.298899 Y271.943753 Z2 E1351.432837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X103.823311 Y269.446117 Z2 E1364.699687 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X102.316477 Y267.115767 Z2 E1377.390882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X100.801375 Y264.95825 Z2 E1389.447681 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X97.838268 Y261.183914 Z2 E1411.392517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X95.117797 Y258.1675 Z2 E1429.969062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X92.823771 Y255.953398 Z2 E1444.549685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X91.14 Y254.586 Z2 E1454.469425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X89.590116 Y252.921193 Z2 E1464.871698 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X88.115416 Y251.484041 Z2 E1474.288797 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X86.713386 Y250.263888 Z2 E1482.788754 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X85.381516 Y249.250078 Z2 E1490.443607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X84.117291 Y248.431953 Z2 E1497.330274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X83.910292 Y248.322662 Z2 E1498.400783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X82.918201 Y247.798857 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X81.781733 Y247.340134 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X80.705375 Y247.045125 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X79.686615 Y246.903175 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X79.178707 Y246.903413 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0002
G0 X79.178707 Y246.903413 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0003 note=intra-page lift
G0 X71.382815 Y257.414957 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0003 note=intra-page XY
G0 X71.382815 Y257.414957 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0003 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0003
G1 X70.834511 Y257.008307 Z2 E1498.471821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X70.13344 Y256.588102 Z2 E1498.743778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X69.17966 Y256.016428 Z2 E1499.440814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X68.828898 Y255.85053 Z2 E1499.772763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X67.472914 Y255.209197 Z2 E1501.487739 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X67.435556 Y255.191528 Z2 E1501.544696 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X66.06215 Y254.700116 Z2 E1503.888705 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X65.618997 Y254.541553 Z2 E1504.783468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X64.620511 Y254.291445 Z2 E1506.975661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X63.747476 Y254.072761 Z2 E1509.157128 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X63.153977 Y253.984724 Z2 E1510.748608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X61.839017 Y253.789668 Z2 E1514.665678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X61.66857 Y253.781295 Z2 E1515.207545 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X60.170377 Y253.707693 Z2 E1520.352472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X59.912 Y253.695 Z2 E1521.309116 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X58.672184 Y253.755908 Z2 E1526.183389 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X57.984983 Y253.789668 Z2 E1529.087444 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X57.181801 Y253.908809 Z2 E1532.700297 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=prime ramp
G1 X56.076524 Y254.072761 Z2 E1537.810334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X54.205003 Y254.541553 Z2 E1546.633728 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X52.388444 Y255.191528 Z2 E1555.457122 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X50.64434 Y256.016428 Z2 E1564.280517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X48.989489 Y257.008307 Z2 E1573.103911 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X47.439828 Y258.157614 Z2 E1581.927305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X46.010281 Y259.453281 Z2 E1590.7507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X44.714614 Y260.882828 Z2 E1599.574094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X43.565307 Y262.432489 Z2 E1608.397488 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X42.573428 Y264.08734 Z2 E1617.220883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X41.748528 Y265.831444 Z2 E1626.044277 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X41.098553 Y267.648003 Z2 E1634.867671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X40.629761 Y269.519524 Z2 E1643.691066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X40.346668 Y271.427983 Z2 E1652.51446 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X40.252 Y273.355 Z2 E1661.337854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X40.346668 Y275.282017 Z2 E1670.161249 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X40.629761 Y277.190476 Z2 E1678.984643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X41.098553 Y279.061997 Z2 E1687.808038 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X41.748528 Y280.878556 Z2 E1696.631432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X42.573428 Y282.62266 Z2 E1705.454826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X43.565307 Y284.277511 Z2 E1714.278221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X44.714614 Y285.827172 Z2 E1723.101615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X46.010281 Y287.256719 Z2 E1731.925009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X47.439828 Y288.552386 Z2 E1740.748404 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X48.989489 Y289.701693 Z2 E1749.571798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X50.64434 Y290.693572 Z2 E1758.395192 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X52.388444 Y291.518472 Z2 E1767.218587 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X54.205003 Y292.168447 Z2 E1776.041981 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X56.076524 Y292.637239 Z2 E1784.865375 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X57.984983 Y292.920332 Z2 E1793.68877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X59.912 Y293.015 Z2 E1802.512164 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X61.839017 Y292.920332 Z2 E1811.335558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X63.747476 Y292.637239 Z2 E1820.158953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X65.618997 Y292.168447 Z2 E1828.982347 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X67.435556 Y291.518472 Z2 E1837.805741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X69.17966 Y290.693572 Z2 E1846.629136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X70.834511 Y289.701693 Z2 E1855.45253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X72.384172 Y288.552386 Z2 E1864.275924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X73.813719 Y287.256719 Z2 E1873.099319 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X75.109386 Y285.827172 Z2 E1881.922713 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X76.258693 Y284.277511 Z2 E1890.746107 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X77.250572 Y282.62266 Z2 E1899.569502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X78.075472 Y280.878556 Z2 E1908.392896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X78.725447 Y279.061997 Z2 E1917.216291 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X79.194239 Y277.190476 Z2 E1926.039685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X79.477332 Y275.282017 Z2 E1934.863079 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X79.572 Y273.355 Z2 E1943.686474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X79.477332 Y271.427983 Z2 E1952.509868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X79.194239 Y269.519524 Z2 E1961.333262 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X78.725447 Y267.648003 Z2 E1970.156657 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X78.075472 Y265.831444 Z2 E1978.980051 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X77.250572 Y264.08734 Z2 E1987.803445 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X76.258693 Y262.432489 Z2 E1996.62684 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X75.109386 Y260.882828 Z2 E2005.450234 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X75.038617 Y260.804747 Z2 E2005.932164 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X73.813719 Y259.453281 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X72.384172 Y258.157614 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
G1 X71.382815 Y257.414957 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0003
G0 X71.382815 Y257.414957 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0004 note=intra-page lift
G0 X81.287865 Y286.308153 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0004 note=intra-page XY
G0 X81.287865 Y286.308153 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0004 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0004
G1 X80.587805 Y286.548145 Z2 E2006.015653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X79.925693 Y286.92114 Z2 E2006.275159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X79.914274 Y286.927573 Z2 E2006.281179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X79.33525 Y287.365 Z2 E2006.696229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X78.845171 Y287.855865 Z2 E2007.243027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X78.80816 Y287.91241 Z2 E2007.304144 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X78.109606 Y288.979661 Z2 E2008.718844 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X78.024216 Y289.187245 Z2 E2009.01912 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.853 Y289.603469 Z2 E2009.667477 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.611562 Y290.625268 Z2 E2011.420086 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.534336 Y290.952098 Z2 E2012.051614 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.457314 Y292.113718 Z2 E2014.507042 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.438 Y292.405 Z2 E2015.187552 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.517927 Y293.610431 Z2 E2018.279989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.534336 Y293.857902 Z2 E2018.969908 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.822236 Y295.076336 Z2 E2022.738926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X77.853 Y295.206531 Z2 E2023.169924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X78.109606 Y295.830339 Z2 E2025.426142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X78.488416 Y296.409084 Z2 E2027.883853 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X78.845171 Y296.954135 Z2 E2030.331857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X79.33525 Y297.445 Z2 E2033.080696 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X79.458879 Y297.538397 Z2 E2033.71477 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X79.914274 Y297.882427 Z2 E2036.113551 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X80.587805 Y298.261855 Z2 E2039.521005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X80.735573 Y298.312513 Z2 E2040.231678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X82.240625 Y298.828469 Z2 E2047.507907 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X83.231036 Y299.006531 Z2 E2052.109943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X85.567663 Y299.129358 Z2 E2062.810719 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X86.925 Y299.065 Z2 E2069.025159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X88.213428 Y299.241977 Z2 E2074.972812 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X90.116984 Y299.286625 Z2 E2083.680682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X92.53933 Y299.120898 Z2 E2094.784616 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X95.384125 Y298.66675 Z2 E2107.959367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X98.555029 Y297.846133 Z2 E2122.938513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X100.232666 Y297.274009 Z2 E2131.044677 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X101.955703 Y296.581 Z2 E2139.538059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X103.712097 Y295.757351 Z2 E2148.409869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X105.489807 Y294.793305 Z2 E2157.65832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X107.276788 Y293.679106 Z2 E2167.289086 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X109.061 Y292.405 Z2 E2177.315667 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X107.276788 Y291.130894 Z2 E2187.342248 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X105.489807 Y290.016695 Z2 E2196.973014 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X103.712097 Y289.052649 Z2 E2206.221464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X101.955703 Y288.229 Z2 E2215.093274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X100.232666 Y287.535991 Z2 E2223.586657 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X98.555029 Y286.963867 Z2 E2231.692821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X95.384125 Y286.14325 Z2 E2246.671966 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X92.53933 Y285.689102 Z2 E2259.846718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X90.116984 Y285.523375 Z2 E2270.950652 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X88.213428 Y285.568023 Z2 E2279.658522 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X86.925 Y285.745 Z2 E2285.606175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X86.213603 Y285.711269 Z2 E2288.863237 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X85.567663 Y285.680642 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X83.231036 Y285.803469 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X82.240625 Y285.981531 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
G1 X81.287865 Y286.308153 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0004
G0 X81.287865 Y286.308153 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0005 note=intra-page lift
G0 X72.384172 Y296.257614 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0005 note=intra-page XY
G0 X72.384172 Y296.257614 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0005 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0005
G1 X71.179361 Y295.364066 Z2 E2289.206232 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X70.834511 Y295.108307 Z2 E2289.430682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X69.916176 Y294.557879 Z2 E2290.235218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X69.17966 Y294.116428 Z2 E2291.133015 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X68.599915 Y293.842229 Z2 E2291.950194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X67.435556 Y293.291528 Z2 E2293.970238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X67.23597 Y293.220115 Z2 E2294.35116 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X65.823654 Y292.714781 Z2 E2297.438116 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X65.618997 Y292.641553 Z2 E2297.94235 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X64.3748 Y292.329898 Z2 E2301.211062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X63.747476 Y292.172761 Z2 E2303.049351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X62.903416 Y292.047557 Z2 E2305.669999 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X61.839017 Y291.889668 Z2 E2309.291241 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X61.415573 Y291.868866 Z2 E2310.814926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X59.91738 Y291.795264 Z2 E2316.645844 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X59.912 Y291.795 Z2 E2316.66802 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X58.419187 Y291.868337 Z2 E2323.162752 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X57.984983 Y291.889668 Z2 E2325.150878 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X56.076524 Y292.172761 Z2 E2333.974272 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X54.205003 Y292.641553 Z2 E2342.797666 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X52.388444 Y293.291528 Z2 E2351.621061 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X50.64434 Y294.116428 Z2 E2360.444455 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X48.989489 Y295.108307 Z2 E2369.26785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X47.439828 Y296.257614 Z2 E2378.091244 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X46.010281 Y297.553281 Z2 E2386.914638 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X44.714614 Y298.982828 Z2 E2395.738033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X43.565307 Y300.532489 Z2 E2404.561427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X42.573428 Y302.18734 Z2 E2413.384821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X41.748528 Y303.931444 Z2 E2422.208216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X41.098553 Y305.748003 Z2 E2431.03161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X40.629761 Y307.619524 Z2 E2439.855004 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X40.346668 Y309.527983 Z2 E2448.678399 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X40.252 Y311.455 Z2 E2457.501793 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X40.346668 Y313.382017 Z2 E2466.325187 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X40.629761 Y315.290476 Z2 E2475.148582 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X41.098553 Y317.161997 Z2 E2483.971976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X41.748528 Y318.978556 Z2 E2492.79537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X42.573428 Y320.72266 Z2 E2501.618765 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X43.565307 Y322.377511 Z2 E2510.442159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X44.714614 Y323.927172 Z2 E2519.265553 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X46.010281 Y325.356719 Z2 E2528.088948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X47.439828 Y326.652386 Z2 E2536.912342 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X48.989489 Y327.801693 Z2 E2545.735736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X50.64434 Y328.793572 Z2 E2554.559131 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X52.388444 Y329.618472 Z2 E2563.382525 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X54.205003 Y330.268447 Z2 E2572.205919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X56.076524 Y330.737239 Z2 E2581.029314 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X57.984983 Y331.020332 Z2 E2589.852708 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X59.912 Y331.115 Z2 E2598.676103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X61.839017 Y331.020332 Z2 E2607.499497 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X63.747476 Y330.737239 Z2 E2616.322891 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X65.618997 Y330.268447 Z2 E2625.146286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X67.435556 Y329.618472 Z2 E2633.96968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X69.17966 Y328.793572 Z2 E2642.793074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X70.834511 Y327.801693 Z2 E2651.616469 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X72.384172 Y326.652386 Z2 E2660.439863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X73.813719 Y325.356719 Z2 E2669.263257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X75.109386 Y323.927172 Z2 E2678.086652 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X76.258693 Y322.377511 Z2 E2686.910046 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X77.250572 Y320.72266 Z2 E2695.73344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X78.075472 Y318.978556 Z2 E2704.556835 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X78.725447 Y317.161997 Z2 E2713.380229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X79.194239 Y315.290476 Z2 E2722.203623 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X79.477332 Y313.382017 Z2 E2731.027018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X79.572 Y311.455 Z2 E2739.850412 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X79.477332 Y309.527983 Z2 E2748.673806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X79.194239 Y307.619524 Z2 E2757.497201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X78.725447 Y305.748003 Z2 E2766.320595 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X78.075472 Y303.931444 Z2 E2775.143989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X77.250572 Y302.18734 Z2 E2783.967384 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X76.258693 Y300.532489 Z2 E2792.790778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X75.789268 Y299.899543 Z2 E2796.394618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X75.109386 Y298.982828 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
G1 X73.813719 Y297.553281 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
G1 X72.384172 Y296.257614 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0005
G0 X72.384172 Y296.257614 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0006 note=intra-page lift
G0 X85.840914 Y311.628732 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0006 note=intra-page XY
G0 X85.840914 Y311.628732 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0006 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0006
G1 X84.72702 Y312.633341 Z2 E2796.737613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X83.613125 Y313.637951 Z2 E2797.766599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X82.8245 Y314.349203 Z2 E2798.909873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X82.520315 Y314.664369 Z2 E2799.481575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X81.478623 Y315.743664 Z2 E2801.882541 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X80.610398 Y316.643229 Z2 E2804.407835 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X80.45293 Y316.83713 Z2 E2804.969497 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X79.507319 Y318.001526 Z2 E2808.742443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X79.243 Y318.327 Z2 E2809.919737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X78.452003 Y319.063393 Z2 E2813.20138 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X77.578193 Y319.876884 Z2 E2817.240561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X77.364531 Y320.096128 Z2 E2818.346307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X76.317635 Y321.170376 Z2 E2824.177225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X76.141041 Y321.351584 Z2 E2825.228423 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X75.322422 Y322.292227 Z2 E2830.694133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X74.920888 Y322.753614 Z2 E2833.491341 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X73.907078 Y324.085484 Z2 E2841.146194 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X73.088953 Y325.349709 Z2 E2848.032861 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X72.455857 Y326.548799 Z2 E2854.23403 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X71.997134 Y327.685267 Z2 E2859.838826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X71.702125 Y328.761625 Z2 E2864.942842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X71.560175 Y329.780385 Z2 E2869.646916 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X71.560627 Y330.744061 Z2 E2874.054062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X71.692824 Y331.655162 Z2 E2878.264407 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X71.946109 Y332.516203 Z2 E2882.369013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X72.309826 Y333.329695 Z2 E2886.444253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X72.773318 Y334.09815 Z2 E2890.548359 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X73.957 Y335.51 Z2 E2898.974129 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X75.36885 Y336.693682 Z2 E2907.399899 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X76.137305 Y337.157174 Z2 E2911.504005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X76.950797 Y337.520891 Z2 E2915.579245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X77.811838 Y337.774176 Z2 E2919.683852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X78.722939 Y337.906373 Z2 E2923.894197 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X79.686615 Y337.906825 Z2 E2928.301342 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X80.705375 Y337.764875 Z2 E2933.005417 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X81.781733 Y337.469866 Z2 E2938.109432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X82.918201 Y337.011143 Z2 E2943.714228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X84.117291 Y336.378047 Z2 E2949.915398 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X85.381516 Y335.559922 Z2 E2956.802065 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X86.713386 Y334.546112 Z2 E2964.456918 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X88.115416 Y333.325959 Z2 E2972.956875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X89.590116 Y331.888807 Z2 E2982.373974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X91.14 Y330.224 Z2 E2992.776247 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X92.823771 Y328.856602 Z2 E3002.695987 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X95.117797 Y326.6425 Z2 E3017.27661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X97.838268 Y323.626086 Z2 E3035.853155 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X100.801375 Y319.85175 Z2 E3057.797991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X102.316477 Y317.694233 Z2 E3069.85479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X103.823311 Y315.363883 Z2 E3082.545985 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X105.298899 Y312.866247 Z2 E3095.812835 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X106.720266 Y310.206875 Z2 E3109.602998 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X108.064435 Y307.391315 Z2 E3123.871426 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X109.308432 Y304.425117 Z2 E3138.581335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X110.429279 Y301.313829 Z2 E3153.705246 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X111.404 Y298.063 Z2 E3169.226068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X108.153171 Y299.037721 Z2 E3184.74689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X105.041883 Y300.158568 Z2 E3199.870801 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X102.075685 Y301.402565 Z2 E3214.58071 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X99.260125 Y302.746734 Z2 E3228.849138 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X96.600753 Y304.168101 Z2 E3242.639301 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X94.103117 Y305.643689 Z2 E3255.906151 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X91.772767 Y307.150523 Z2 E3268.597347 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X89.78015 Y308.549825 Z2 E3279.732639 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X89.61525 Y308.665625 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X85.840914 Y311.628732 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0006
G0 X85.840914 Y311.628732 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0007 note=intra-page lift
G0 X92.305003 Y330.741553 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0007 note=intra-page XY
G0 X92.305003 Y330.741553 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0007 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0007
G1 X90.892687 Y331.246888 Z2 E3280.075634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X90.488444 Y331.391528 Z2 E3280.300083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X89.520579 Y331.849294 Z2 E3281.104619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X88.74434 Y332.216428 Z2 E3282.002417 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X88.194263 Y332.546131 Z2 E3282.819595 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X87.089489 Y333.208307 Z2 E3284.83964 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X86.919228 Y333.334582 Z2 E3285.220561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X85.714416 Y334.228131 Z2 E3288.307517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X85.539828 Y334.357614 Z2 E3288.811751 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X84.589457 Y335.21898 Z2 E3292.080464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X84.110281 Y335.653281 Z2 E3293.918752 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X83.537243 Y336.285531 Z2 E3296.539401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X82.814614 Y337.082828 Z2 E3300.160642 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X82.562065 Y337.423351 Z2 E3301.684328 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X81.668516 Y338.628163 Z2 E3307.515245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X81.665307 Y338.632489 Z2 E3307.537421 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X80.896923 Y339.914462 Z2 E3314.032153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X80.673428 Y340.28734 Z2 E3316.020279 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X79.848528 Y342.031444 Z2 E3324.843674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X79.198553 Y343.848003 Z2 E3333.667068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X78.729761 Y345.719524 Z2 E3342.490462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X78.446668 Y347.627983 Z2 E3351.313857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X78.352 Y349.555 Z2 E3360.137251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X78.446668 Y351.482017 Z2 E3368.960645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X78.729761 Y353.390476 Z2 E3377.78404 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X79.198553 Y355.261997 Z2 E3386.607434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X79.848528 Y357.078556 Z2 E3395.430828 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X80.673428 Y358.82266 Z2 E3404.254223 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X81.665307 Y360.477511 Z2 E3413.077617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X82.814614 Y362.027172 Z2 E3421.901012 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X84.110281 Y363.456719 Z2 E3430.724406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X85.539828 Y364.752386 Z2 E3439.5478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X87.089489 Y365.901693 Z2 E3448.371195 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X88.74434 Y366.893572 Z2 E3457.194589 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X90.488444 Y367.718472 Z2 E3466.017983 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X92.305003 Y368.368447 Z2 E3474.841378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X94.176524 Y368.837239 Z2 E3483.664772 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X96.084983 Y369.120332 Z2 E3492.488166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X98.012 Y369.215 Z2 E3501.311561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X99.939017 Y369.120332 Z2 E3510.134955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X101.847476 Y368.837239 Z2 E3518.958349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X103.718997 Y368.368447 Z2 E3527.781744 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X105.535556 Y367.718472 Z2 E3536.605138 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X107.27966 Y366.893572 Z2 E3545.428532 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X108.934511 Y365.901693 Z2 E3554.251927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X110.484172 Y364.752386 Z2 E3563.075321 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X111.913719 Y363.456719 Z2 E3571.898715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X113.209386 Y362.027172 Z2 E3580.72211 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X114.358693 Y360.477511 Z2 E3589.545504 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X115.350572 Y358.82266 Z2 E3598.368898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X116.175472 Y357.078556 Z2 E3607.192293 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X116.825447 Y355.261997 Z2 E3616.015687 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X117.294239 Y353.390476 Z2 E3624.839081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X117.577332 Y351.482017 Z2 E3633.662476 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X117.672 Y349.555 Z2 E3642.48587 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X117.577332 Y347.627983 Z2 E3651.309265 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X117.294239 Y345.719524 Z2 E3660.132659 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X116.825447 Y343.848003 Z2 E3668.956053 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X116.175472 Y342.031444 Z2 E3677.779448 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X115.350572 Y340.28734 Z2 E3686.602842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X114.358693 Y338.632489 Z2 E3695.426236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X113.209386 Y337.082828 Z2 E3704.249631 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X111.913719 Y335.653281 Z2 E3713.073025 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X110.484172 Y334.357614 Z2 E3721.896419 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X108.934511 Y333.208307 Z2 E3730.719814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X107.27966 Y332.216428 Z2 E3739.543208 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X105.535556 Y331.391528 Z2 E3748.366602 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X103.718997 Y330.741553 Z2 E3757.189997 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X101.847476 Y330.272761 Z2 E3766.013391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X99.939017 Y329.989668 Z2 E3774.836785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X98.012 Y329.895 Z2 E3783.66018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X97.224926 Y329.933666 Z2 E3787.26402 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X96.084983 Y329.989668 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
G1 X94.176524 Y330.272761 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
G1 X92.305003 Y330.741553 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0007
G0 X92.305003 Y330.741553 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0008 note=intra-page lift
G0 X77.020166 Y339.902932 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0008 note=intra-page XY
G0 X77.020166 Y339.902932 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0008 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0008
G1 X76.258693 Y338.632489 Z2 E3787.598458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X76.247476 Y338.617365 Z2 E3787.607015 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X75.353927 Y337.412554 Z2 E3788.636 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X75.109386 Y337.082828 Z2 E3789.037166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X74.37773 Y336.27557 Z2 E3790.350976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X73.813719 Y335.653281 Z2 E3791.610763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X73.324582 Y335.209953 Z2 E3792.751942 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X72.384172 Y334.357614 Z2 E3795.319249 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X72.198786 Y334.220123 Z2 E3795.838898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X70.993975 Y333.326574 Z2 E3799.611845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X70.834511 Y333.208307 Z2 E3800.162624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X69.718207 Y332.53922 Z2 E3804.070782 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X69.17966 Y332.216428 Z2 E3806.140889 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X68.391269 Y331.843547 Z2 E3809.215709 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X67.435556 Y331.391528 Z2 E3813.254042 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X67.018656 Y331.242359 Z2 E3815.046626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X65.618997 Y330.741553 Z2 E3821.502085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X65.605957 Y330.738287 Z2 E3821.563534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X63.747476 Y330.272761 Z2 E3830.325451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X61.839017 Y329.989668 Z2 E3839.148846 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X59.912 Y329.895 Z2 E3847.97224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X57.984983 Y329.989668 Z2 E3856.795634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X56.076524 Y330.272761 Z2 E3865.619029 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X54.205003 Y330.741553 Z2 E3874.442423 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X52.388444 Y331.391528 Z2 E3883.265817 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X50.64434 Y332.216428 Z2 E3892.089212 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X48.989489 Y333.208307 Z2 E3900.912606 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X47.439828 Y334.357614 Z2 E3909.736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X46.010281 Y335.653281 Z2 E3918.559395 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X44.714614 Y337.082828 Z2 E3927.382789 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X43.565307 Y338.632489 Z2 E3936.206183 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X42.573428 Y340.28734 Z2 E3945.029578 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X41.748528 Y342.031444 Z2 E3953.852972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X41.098553 Y343.848003 Z2 E3962.676367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X40.629761 Y345.719524 Z2 E3971.499761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X40.346668 Y347.627983 Z2 E3980.323155 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X40.252 Y349.555 Z2 E3989.14655 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X40.346668 Y351.482017 Z2 E3997.969944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X40.629761 Y353.390476 Z2 E4006.793338 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X41.098553 Y355.261997 Z2 E4015.616733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X41.748528 Y357.078556 Z2 E4024.440127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X42.573428 Y358.82266 Z2 E4033.263521 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X43.565307 Y360.477511 Z2 E4042.086916 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X44.714614 Y362.027172 Z2 E4050.91031 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X46.010281 Y363.456719 Z2 E4059.733704 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X47.439828 Y364.752386 Z2 E4068.557099 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X48.989489 Y365.901693 Z2 E4077.380493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X50.64434 Y366.893572 Z2 E4086.203887 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X52.388444 Y367.718472 Z2 E4095.027282 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X54.205003 Y368.368447 Z2 E4103.850676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X56.076524 Y368.837239 Z2 E4112.67407 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X57.984983 Y369.120332 Z2 E4121.497465 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X59.912 Y369.215 Z2 E4130.320859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X61.839017 Y369.120332 Z2 E4139.144253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X63.747476 Y368.837239 Z2 E4147.967648 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X65.618997 Y368.368447 Z2 E4156.791042 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X67.435556 Y367.718472 Z2 E4165.614436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X69.17966 Y366.893572 Z2 E4174.437831 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X70.834511 Y365.901693 Z2 E4183.261225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X72.384172 Y364.752386 Z2 E4192.08462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X73.813719 Y363.456719 Z2 E4200.908014 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X75.109386 Y362.027172 Z2 E4209.731408 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X76.258693 Y360.477511 Z2 E4218.554803 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X77.250572 Y358.82266 Z2 E4227.378197 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X78.075472 Y357.078556 Z2 E4236.201591 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X78.725447 Y355.261997 Z2 E4245.024986 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X79.194239 Y353.390476 Z2 E4253.84838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X79.477332 Y351.482017 Z2 E4262.671774 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X79.572 Y349.555 Z2 E4271.495169 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X79.477332 Y347.627983 Z2 E4280.318563 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X79.194239 Y345.719524 Z2 E4289.141957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X78.893868 Y344.520378 Z2 E4294.795401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X78.725447 Y343.848003 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X78.075472 Y342.031444 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X77.250572 Y340.28734 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
G1 X77.020166 Y339.902932 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0008
G0 X77.020166 Y339.902932 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0009 note=intra-page lift
G0 X110.991814 Y328.256907 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0009 note=intra-page XY
G0 X110.991814 Y328.256907 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0009 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0009
G1 X111.205145 Y328.879195 Z2 E4294.861371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X111.584573 Y329.552726 Z2 E4295.107519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X111.62623 Y329.607868 Z2 E4295.138396 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X112.022 Y330.13175 Z2 E4295.50438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X112.512865 Y330.621829 Z2 E4296.033791 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X112.6382 Y330.703865 Z2 E4296.167382 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X113.636661 Y331.357394 Z2 E4297.475941 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X113.920278 Y331.474061 Z2 E4297.882357 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X114.260469 Y331.614 Z2 E4298.407666 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X115.36228 Y331.874344 Z2 E4300.283323 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X115.609098 Y331.932664 Z2 E4300.757067 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X116.852752 Y332.015126 Z2 E4303.37028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X117.062 Y332.029 Z2 E4303.856507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X118.349466 Y331.943633 Z2 E4307.143226 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X118.514902 Y331.932664 Z2 E4307.602365 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X119.813347 Y331.625858 Z2 E4311.602163 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X119.863531 Y331.614 Z2 E4311.767645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X120.487339 Y331.357394 Z2 E4314.006956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X121.134874 Y330.933559 Z2 E4316.74709 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X121.611135 Y330.621829 Z2 E4318.879004 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X122.102 Y330.13175 Z2 E4321.610457 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X122.244954 Y329.942521 Z2 E4322.578007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X122.539427 Y329.552726 Z2 E4324.625122 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X122.918855 Y328.879195 Z2 E4328.013199 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X122.996174 Y328.653655 Z2 E4329.094915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=prime ramp
G1 X123.485469 Y327.226375 Z2 E4335.995154 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X123.663531 Y326.235964 Z2 E4340.59719 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X123.786358 Y323.899337 Z2 E4351.297966 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X123.722 Y322.542 Z2 E4357.512406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X123.898977 Y321.253572 Z2 E4363.460059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X123.943625 Y319.350016 Z2 E4372.167929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X123.777898 Y316.92767 Z2 E4383.271863 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X123.32375 Y314.082875 Z2 E4396.446615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X122.503133 Y310.911971 Z2 E4411.42576 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X121.931009 Y309.234334 Z2 E4419.531924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X121.238 Y307.511297 Z2 E4428.025307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X120.414351 Y305.754903 Z2 E4436.897117 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X119.450305 Y303.977193 Z2 E4446.145567 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X118.336106 Y302.190212 Z2 E4455.776333 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X117.062 Y300.406 Z2 E4465.802914 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X115.787894 Y302.190212 Z2 E4475.829495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X114.673695 Y303.977193 Z2 E4485.460261 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X113.709649 Y305.754903 Z2 E4494.708711 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X112.886 Y307.511297 Z2 E4503.580522 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X112.192991 Y309.234334 Z2 E4512.073904 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X111.620867 Y310.911971 Z2 E4520.180068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X110.80025 Y314.082875 Z2 E4535.159214 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X110.346102 Y316.92767 Z2 E4548.333965 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X110.180375 Y319.350016 Z2 E4559.437899 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X110.225023 Y321.253572 Z2 E4568.145769 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X110.402 Y322.542 Z2 E4574.093422 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X110.364375 Y323.335519 Z2 E4577.726475 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X110.337642 Y323.899337 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X110.460469 Y326.235964 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X110.638531 Y327.226375 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X110.991814 Y328.256907 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0009
G0 X110.991814 Y328.256907 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0010 note=intra-page lift
G0 X120.914614 Y337.082828 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0010 note=intra-page XY
G0 X120.914614 Y337.082828 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0010 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0010
G1 X120.021066 Y338.287639 Z2 E4578.06947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X119.765307 Y338.632489 Z2 E4578.293919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X119.214879 Y339.550824 Z2 E4579.098455 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X118.773428 Y340.28734 Z2 E4579.996253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X118.499229 Y340.867085 Z2 E4580.813431 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X117.948528 Y342.031444 Z2 E4582.833475 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X117.877115 Y342.23103 Z2 E4583.214397 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X117.371781 Y343.643346 Z2 E4586.301353 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X117.298553 Y343.848003 Z2 E4586.805587 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.986898 Y345.0922 Z2 E4590.0743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.829761 Y345.719524 Z2 E4591.912588 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.704557 Y346.563584 Z2 E4594.533237 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.546668 Y347.627983 Z2 E4598.154478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.525866 Y348.051427 Z2 E4599.678164 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.452264 Y349.54962 Z2 E4605.509081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.452 Y349.555 Z2 E4605.531257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.525337 Y351.047813 Z2 E4612.025989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=prime ramp
G1 X116.546668 Y351.482017 Z2 E4614.014115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X116.829761 Y353.390476 Z2 E4622.837509 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X117.298553 Y355.261997 Z2 E4631.660904 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X117.948528 Y357.078556 Z2 E4640.484298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X118.773428 Y358.82266 Z2 E4649.307692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X119.765307 Y360.477511 Z2 E4658.131087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X120.914614 Y362.027172 Z2 E4666.954481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X122.210281 Y363.456719 Z2 E4675.777876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X123.639828 Y364.752386 Z2 E4684.60127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X125.189489 Y365.901693 Z2 E4693.424664 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X126.84434 Y366.893572 Z2 E4702.248059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X128.588444 Y367.718472 Z2 E4711.071453 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X130.405003 Y368.368447 Z2 E4719.894847 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X132.276524 Y368.837239 Z2 E4728.718242 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X134.184983 Y369.120332 Z2 E4737.541636 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X136.112 Y369.215 Z2 E4746.36503 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X138.039017 Y369.120332 Z2 E4755.188425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X139.947476 Y368.837239 Z2 E4764.011819 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X141.818997 Y368.368447 Z2 E4772.835213 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X143.635556 Y367.718472 Z2 E4781.658608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X145.37966 Y366.893572 Z2 E4790.482002 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X147.034511 Y365.901693 Z2 E4799.305396 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X148.584172 Y364.752386 Z2 E4808.128791 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X150.013719 Y363.456719 Z2 E4816.952185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X151.309386 Y362.027172 Z2 E4825.775579 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X152.458693 Y360.477511 Z2 E4834.598974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X153.450572 Y358.82266 Z2 E4843.422368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X154.275472 Y357.078556 Z2 E4852.245762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X154.925447 Y355.261997 Z2 E4861.069157 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X155.394239 Y353.390476 Z2 E4869.892551 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X155.677332 Y351.482017 Z2 E4878.715945 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X155.772 Y349.555 Z2 E4887.53934 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X155.677332 Y347.627983 Z2 E4896.362734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X155.394239 Y345.719524 Z2 E4905.186129 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X154.925447 Y343.848003 Z2 E4914.009523 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X154.275472 Y342.031444 Z2 E4922.832917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X153.450572 Y340.28734 Z2 E4931.656312 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X152.458693 Y338.632489 Z2 E4940.479706 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X151.309386 Y337.082828 Z2 E4949.3031 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X150.013719 Y335.653281 Z2 E4958.126495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X148.584172 Y334.357614 Z2 E4966.949889 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X147.034511 Y333.208307 Z2 E4975.773283 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X145.37966 Y332.216428 Z2 E4984.596678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X143.635556 Y331.391528 Z2 E4993.420072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X141.818997 Y330.741553 Z2 E5002.243466 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X139.947476 Y330.272761 Z2 E5011.066861 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X138.039017 Y329.989668 Z2 E5019.890255 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X136.112 Y329.895 Z2 E5028.713649 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X134.184983 Y329.989668 Z2 E5037.537044 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X132.276524 Y330.272761 Z2 E5046.360438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X130.405003 Y330.741553 Z2 E5055.183832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X128.588444 Y331.391528 Z2 E5064.007227 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X126.84434 Y332.216428 Z2 E5072.830621 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X125.189489 Y333.208307 Z2 E5081.654015 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X124.556543 Y333.677732 Z2 E5085.257856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X123.639828 Y334.357614 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X122.210281 Y335.653281 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
G1 X120.914614 Y337.082828 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0010
G0 X120.914614 Y337.082828 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0011 note=intra-page lift
G0 X136.285732 Y323.626086 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0011 note=intra-page XY
G0 X136.285732 Y323.626086 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0011 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0011
G1 X137.290341 Y324.73998 Z2 E5085.600851 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X138.294951 Y325.853875 Z2 E5086.629836 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X139.006203 Y326.6425 Z2 E5087.77311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X139.321369 Y326.946685 Z2 E5088.344812 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X140.400664 Y327.988377 Z2 E5090.745778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X141.300229 Y328.856602 Z2 E5093.271072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X141.49413 Y329.01407 Z2 E5093.832734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X142.658526 Y329.959681 Z2 E5097.605681 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X142.984 Y330.224 Z2 E5098.782974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X143.720393 Y331.014997 Z2 E5102.064618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X144.533884 Y331.888807 Z2 E5106.103798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X144.753128 Y332.102469 Z2 E5107.209545 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X145.827376 Y333.149365 Z2 E5113.040462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X146.008584 Y333.325959 Z2 E5114.09166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X146.949227 Y334.144578 Z2 E5119.55737 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X147.410614 Y334.546112 Z2 E5122.354578 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X148.742484 Y335.559922 Z2 E5130.009431 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X150.006709 Y336.378047 Z2 E5136.896098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X151.205799 Y337.011143 Z2 E5143.097267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X152.342267 Y337.469866 Z2 E5148.702064 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X153.418625 Y337.764875 Z2 E5153.806079 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X154.437385 Y337.906825 Z2 E5158.510154 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X155.401061 Y337.906373 Z2 E5162.917299 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X156.312162 Y337.774176 Z2 E5167.127644 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X157.173203 Y337.520891 Z2 E5171.232251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X157.986695 Y337.157174 Z2 E5175.30749 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X158.75515 Y336.693682 Z2 E5179.411597 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X160.167 Y335.51 Z2 E5187.837367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X161.350682 Y334.09815 Z2 E5196.263136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X161.814174 Y333.329695 Z2 E5200.367243 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X162.177891 Y332.516203 Z2 E5204.442482 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X162.431176 Y331.655162 Z2 E5208.547089 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X162.563373 Y330.744061 Z2 E5212.757434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X162.563825 Y329.780385 Z2 E5217.164579 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X162.421875 Y328.761625 Z2 E5221.868654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X162.126866 Y327.685267 Z2 E5226.97267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X161.668143 Y326.548799 Z2 E5232.577466 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X161.035047 Y325.349709 Z2 E5238.778635 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X160.216922 Y324.085484 Z2 E5245.665302 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X159.203112 Y322.753614 Z2 E5253.320155 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X157.982959 Y321.351584 Z2 E5261.820112 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X156.545807 Y319.876884 Z2 E5271.237211 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X154.881 Y318.327 Z2 E5281.639485 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X153.513602 Y316.643229 Z2 E5291.559225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X151.2995 Y314.349203 Z2 E5306.139848 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X148.283086 Y311.628732 Z2 E5324.716392 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X144.50875 Y308.665625 Z2 E5346.661228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X142.351233 Y307.150523 Z2 E5358.718027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X140.020883 Y305.643689 Z2 E5371.409222 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X137.523247 Y304.168101 Z2 E5384.676072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X134.863875 Y302.746734 Z2 E5398.466236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X132.048315 Y301.402565 Z2 E5412.734663 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X129.082117 Y300.158568 Z2 E5427.444572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X125.970829 Y299.037721 Z2 E5442.568484 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X122.72 Y298.063 Z2 E5458.089305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X123.694721 Y301.313829 Z2 E5473.610127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X124.815568 Y304.425117 Z2 E5488.734039 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X126.059565 Y307.391315 Z2 E5503.443947 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X127.403734 Y310.206875 Z2 E5517.712375 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X128.825101 Y312.866247 Z2 E5531.502538 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X130.300689 Y315.363883 Z2 E5544.769388 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X131.807523 Y317.694233 Z2 E5557.460584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X133.206825 Y319.68685 Z2 E5568.595876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X133.322625 Y319.85175 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=end-early tail
G1 X136.285732 Y323.626086 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0011
G0 X136.285732 Y323.626086 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0012 note=intra-page lift
G0 X155.398553 Y317.161997 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0012 note=intra-page XY
G0 X155.398553 Y317.161997 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0012 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0012
G1 X155.903888 Y318.574313 Z2 E5568.938871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X156.048528 Y318.978556 Z2 E5569.163321 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X156.506294 Y319.946421 Z2 E5569.967857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X156.873428 Y320.72266 Z2 E5570.865654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X157.203131 Y321.272737 Z2 E5571.682832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X157.865307 Y322.377511 Z2 E5573.702877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X157.991582 Y322.547772 Z2 E5574.083798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X158.885131 Y323.752584 Z2 E5577.170755 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X159.014614 Y323.927172 Z2 E5577.674989 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X159.87598 Y324.877543 Z2 E5580.943701 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X160.310281 Y325.356719 Z2 E5582.78199 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X160.942531 Y325.929757 Z2 E5585.402638 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X161.739828 Y326.652386 Z2 E5589.023879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X162.080351 Y326.904935 Z2 E5590.547565 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X163.285163 Y327.798484 Z2 E5596.378483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X163.289489 Y327.801693 Z2 E5596.400658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X164.571462 Y328.570077 Z2 E5602.89539 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X164.94434 Y328.793572 Z2 E5604.883517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X166.688444 Y329.618472 Z2 E5613.706911 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X168.505003 Y330.268447 Z2 E5622.530305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X170.376524 Y330.737239 Z2 E5631.3537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X172.284983 Y331.020332 Z2 E5640.177094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X174.212 Y331.115 Z2 E5649.000488 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X176.139017 Y331.020332 Z2 E5657.823883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X178.047476 Y330.737239 Z2 E5666.647277 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X179.918997 Y330.268447 Z2 E5675.470671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X181.735556 Y329.618472 Z2 E5684.294066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X183.47966 Y328.793572 Z2 E5693.11746 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X185.134511 Y327.801693 Z2 E5701.940854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X186.684172 Y326.652386 Z2 E5710.764249 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X188.113719 Y325.356719 Z2 E5719.587643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X189.409386 Y323.927172 Z2 E5728.411038 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X190.558693 Y322.377511 Z2 E5737.234432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X191.550572 Y320.72266 Z2 E5746.057826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X192.375472 Y318.978556 Z2 E5754.881221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X193.025447 Y317.161997 Z2 E5763.704615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X193.494239 Y315.290476 Z2 E5772.528009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X193.777332 Y313.382017 Z2 E5781.351404 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X193.872 Y311.455 Z2 E5790.174798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X193.777332 Y309.527983 Z2 E5798.998192 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X193.494239 Y307.619524 Z2 E5807.821587 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X193.025447 Y305.748003 Z2 E5816.644981 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X192.375472 Y303.931444 Z2 E5825.468375 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X191.550572 Y302.18734 Z2 E5834.29177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X190.558693 Y300.532489 Z2 E5843.115164 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X189.409386 Y298.982828 Z2 E5851.938558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X188.113719 Y297.553281 Z2 E5860.761953 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X186.684172 Y296.257614 Z2 E5869.585347 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X185.134511 Y295.108307 Z2 E5878.408741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X183.47966 Y294.116428 Z2 E5887.232136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X181.735556 Y293.291528 Z2 E5896.05553 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X179.918997 Y292.641553 Z2 E5904.878924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X178.047476 Y292.172761 Z2 E5913.702319 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X176.139017 Y291.889668 Z2 E5922.525713 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X174.212 Y291.795 Z2 E5931.349107 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X172.284983 Y291.889668 Z2 E5940.172502 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X170.376524 Y292.172761 Z2 E5948.995896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X168.505003 Y292.641553 Z2 E5957.819291 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X166.688444 Y293.291528 Z2 E5966.642685 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X164.94434 Y294.116428 Z2 E5975.466079 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X163.289489 Y295.108307 Z2 E5984.289474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X161.739828 Y296.257614 Z2 E5993.112868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X160.310281 Y297.553281 Z2 E6001.936262 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X159.014614 Y298.982828 Z2 E6010.759657 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X157.865307 Y300.532489 Z2 E6019.583051 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X156.873428 Y302.18734 Z2 E6028.406445 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X156.048528 Y303.931444 Z2 E6037.22984 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X155.398553 Y305.748003 Z2 E6046.053234 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X154.929761 Y307.619524 Z2 E6054.876628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X154.646668 Y309.527983 Z2 E6063.700023 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X154.552 Y311.455 Z2 E6072.523417 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X154.590666 Y312.242074 Z2 E6076.127257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X154.646668 Y313.382017 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
G1 X154.929761 Y315.290476 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
G1 X155.398553 Y317.161997 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0012
G0 X155.398553 Y317.161997 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0013 note=intra-page lift
G0 X164.559932 Y332.446834 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0013 note=intra-page XY
G0 X164.559932 Y332.446834 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0013 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0013
G1 X163.289489 Y333.208307 Z2 E6076.461695 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X163.274365 Y333.219524 Z2 E6076.470252 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X162.069554 Y334.113073 Z2 E6077.499238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X161.739828 Y334.357614 Z2 E6077.900403 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X160.93257 Y335.08927 Z2 E6079.214213 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X160.310281 Y335.653281 Z2 E6080.474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X159.866953 Y336.142418 Z2 E6081.615179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X159.014614 Y337.082828 Z2 E6084.182486 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X158.877123 Y337.268214 Z2 E6084.702136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X157.983574 Y338.473025 Z2 E6088.475082 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X157.865307 Y338.632489 Z2 E6089.025862 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X157.19622 Y339.748793 Z2 E6092.934019 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X156.873428 Y340.28734 Z2 E6095.004126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X156.500547 Y341.075731 Z2 E6098.078946 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X156.048528 Y342.031444 Z2 E6102.117279 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X155.899359 Y342.448344 Z2 E6103.909864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X155.398553 Y343.848003 Z2 E6110.365322 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X155.395287 Y343.861043 Z2 E6110.426771 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X154.929761 Y345.719524 Z2 E6119.188689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X154.646668 Y347.627983 Z2 E6128.012083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X154.552 Y349.555 Z2 E6136.835477 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X154.646668 Y351.482017 Z2 E6145.658872 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X154.929761 Y353.390476 Z2 E6154.482266 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X155.398553 Y355.261997 Z2 E6163.30566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X156.048528 Y357.078556 Z2 E6172.129055 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X156.873428 Y358.82266 Z2 E6180.952449 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X157.865307 Y360.477511 Z2 E6189.775843 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X159.014614 Y362.027172 Z2 E6198.599238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X160.310281 Y363.456719 Z2 E6207.422632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X161.739828 Y364.752386 Z2 E6216.246026 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X163.289489 Y365.901693 Z2 E6225.069421 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X164.94434 Y366.893572 Z2 E6233.892815 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X166.688444 Y367.718472 Z2 E6242.716209 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X168.505003 Y368.368447 Z2 E6251.539604 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X170.376524 Y368.837239 Z2 E6260.362998 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X172.284983 Y369.120332 Z2 E6269.186393 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X174.212 Y369.215 Z2 E6278.009787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X176.139017 Y369.120332 Z2 E6286.833181 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X178.047476 Y368.837239 Z2 E6295.656576 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X179.918997 Y368.368447 Z2 E6304.47997 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X181.735556 Y367.718472 Z2 E6313.303364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X183.47966 Y366.893572 Z2 E6322.126759 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X185.134511 Y365.901693 Z2 E6330.950153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X186.684172 Y364.752386 Z2 E6339.773547 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X188.113719 Y363.456719 Z2 E6348.596942 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X189.409386 Y362.027172 Z2 E6357.420336 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X190.558693 Y360.477511 Z2 E6366.24373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X191.550572 Y358.82266 Z2 E6375.067125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X192.375472 Y357.078556 Z2 E6383.890519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X193.025447 Y355.261997 Z2 E6392.713913 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X193.494239 Y353.390476 Z2 E6401.537308 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X193.777332 Y351.482017 Z2 E6410.360702 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X193.872 Y349.555 Z2 E6419.184096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X193.777332 Y347.627983 Z2 E6428.007491 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X193.494239 Y345.719524 Z2 E6436.830885 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X193.025447 Y343.848003 Z2 E6445.654279 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X192.375472 Y342.031444 Z2 E6454.477674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X191.550572 Y340.28734 Z2 E6463.301068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X190.558693 Y338.632489 Z2 E6472.124462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X189.409386 Y337.082828 Z2 E6480.947857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X188.113719 Y335.653281 Z2 E6489.771251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X186.684172 Y334.357614 Z2 E6498.594645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X185.134511 Y333.208307 Z2 E6507.41804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X183.47966 Y332.216428 Z2 E6516.241434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X181.735556 Y331.391528 Z2 E6525.064829 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X179.918997 Y330.741553 Z2 E6533.888223 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X178.047476 Y330.272761 Z2 E6542.711617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X176.139017 Y329.989668 Z2 E6551.535012 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X174.212 Y329.895 Z2 E6560.358406 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X172.284983 Y329.989668 Z2 E6569.1818 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X170.376524 Y330.272761 Z2 E6578.005195 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X169.177378 Y330.573132 Z2 E6583.658638 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X168.505003 Y330.741553 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
G1 X166.688444 Y331.391528 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
G1 X164.94434 Y332.216428 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
G1 X164.559932 Y332.446834 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0013
G0 X164.559932 Y332.446834 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0014 note=intra-page lift
G0 X152.913907 Y298.475186 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0014 note=intra-page XY
G0 X152.913907 Y298.475186 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0014 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0014
G1 X153.536195 Y298.261855 Z2 E6583.724608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X154.209726 Y297.882427 Z2 E6583.970756 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X154.264868 Y297.84077 Z2 E6584.001633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X154.78875 Y297.445 Z2 E6584.367617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X155.278829 Y296.954135 Z2 E6584.897028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X155.360865 Y296.8288 Z2 E6585.030619 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.014394 Y295.830339 Z2 E6586.339179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.131061 Y295.546722 Z2 E6586.745595 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.271 Y295.206531 Z2 E6587.270903 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.531344 Y294.10472 Z2 E6589.146561 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.589664 Y293.857902 Z2 E6589.620305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.672126 Y292.614248 Z2 E6592.233517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.686 Y292.405 Z2 E6592.719745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.600633 Y291.117534 Z2 E6596.006463 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.589664 Y290.952098 Z2 E6596.465603 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.282858 Y289.653653 Z2 E6600.4654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.271 Y289.603469 Z2 E6600.630882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X156.014394 Y288.979661 Z2 E6602.870193 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X155.590559 Y288.332126 Z2 E6605.610327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X155.278829 Y287.855865 Z2 E6607.742241 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X154.78875 Y287.365 Z2 E6610.473694 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X154.599521 Y287.222046 Z2 E6611.441245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X154.209726 Y286.927573 Z2 E6613.488359 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X153.536195 Y286.548145 Z2 E6616.876436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X153.310655 Y286.470826 Z2 E6617.958152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X151.883375 Y285.981531 Z2 E6624.858391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X150.892964 Y285.803469 Z2 E6629.460427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X148.556337 Y285.680642 Z2 E6640.161204 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X147.199 Y285.745 Z2 E6646.375644 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X145.910572 Y285.568023 Z2 E6652.323296 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X144.007016 Y285.523375 Z2 E6661.031166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X141.58467 Y285.689102 Z2 E6672.1351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X138.739875 Y286.14325 Z2 E6685.309852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X135.568971 Y286.963867 Z2 E6700.288997 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X133.891334 Y287.535991 Z2 E6708.395161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X132.168297 Y288.229 Z2 E6716.888544 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X130.411903 Y289.052649 Z2 E6725.760354 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X128.634193 Y290.016695 Z2 E6735.008804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X126.847212 Y291.130894 Z2 E6744.63957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X125.063 Y292.405 Z2 E6754.666151 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X126.847212 Y293.679106 Z2 E6764.692732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X128.634193 Y294.793305 Z2 E6774.323499 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X130.411903 Y295.757351 Z2 E6783.571949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X132.168297 Y296.581 Z2 E6792.443759 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X133.891334 Y297.274009 Z2 E6800.937141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X135.568971 Y297.846133 Z2 E6809.043306 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X138.739875 Y298.66675 Z2 E6824.022451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X141.58467 Y299.120898 Z2 E6837.197203 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X144.007016 Y299.286625 Z2 E6848.301136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X145.910572 Y299.241977 Z2 E6857.009006 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X147.199 Y299.065 Z2 E6862.956659 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X147.992519 Y299.102625 Z2 E6866.589712 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X148.556337 Y299.129358 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X150.892964 Y299.006531 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X151.883375 Y298.828469 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X152.913907 Y298.475186 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0014
G0 X152.913907 Y298.475186 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0015 note=intra-page lift
G0 X161.739828 Y288.552386 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0015 note=intra-page XY
G0 X161.739828 Y288.552386 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0015 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0015
G1 X162.944639 Y289.445934 Z2 E6866.932707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X163.289489 Y289.701693 Z2 E6867.157156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X164.207824 Y290.252121 Z2 E6867.961692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X164.94434 Y290.693572 Z2 E6868.85949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X165.524085 Y290.967771 Z2 E6869.676668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X166.688444 Y291.518472 Z2 E6871.696713 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X166.88803 Y291.589885 Z2 E6872.077634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X168.300346 Y292.095219 Z2 E6875.16459 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X168.505003 Y292.168447 Z2 E6875.668824 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X169.7492 Y292.480102 Z2 E6878.937537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X170.376524 Y292.637239 Z2 E6880.775825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X171.220584 Y292.762443 Z2 E6883.396474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X172.284983 Y292.920332 Z2 E6887.017715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X172.708427 Y292.941134 Z2 E6888.541401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X174.20662 Y293.014736 Z2 E6894.372318 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X174.212 Y293.015 Z2 E6894.394494 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X175.704813 Y292.941663 Z2 E6900.889226 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X176.139017 Y292.920332 Z2 E6902.877352 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X178.047476 Y292.637239 Z2 E6911.700747 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X179.918997 Y292.168447 Z2 E6920.524141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X181.735556 Y291.518472 Z2 E6929.347535 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X183.47966 Y290.693572 Z2 E6938.17093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X185.134511 Y289.701693 Z2 E6946.994324 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X186.684172 Y288.552386 Z2 E6955.817718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X188.113719 Y287.256719 Z2 E6964.641113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X189.409386 Y285.827172 Z2 E6973.464507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X190.558693 Y284.277511 Z2 E6982.287901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X191.550572 Y282.62266 Z2 E6991.111296 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X192.375472 Y280.878556 Z2 E6999.93469 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X193.025447 Y279.061997 Z2 E7008.758085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X193.494239 Y277.190476 Z2 E7017.581479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X193.777332 Y275.282017 Z2 E7026.404873 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X193.872 Y273.355 Z2 E7035.228268 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X193.777332 Y271.427983 Z2 E7044.051662 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X193.494239 Y269.519524 Z2 E7052.875056 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X193.025447 Y267.648003 Z2 E7061.698451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X192.375472 Y265.831444 Z2 E7070.521845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X191.550572 Y264.08734 Z2 E7079.345239 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X190.558693 Y262.432489 Z2 E7088.168634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X189.409386 Y260.882828 Z2 E7096.992028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X188.113719 Y259.453281 Z2 E7105.815422 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X186.684172 Y258.157614 Z2 E7114.638817 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X185.134511 Y257.008307 Z2 E7123.462211 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X183.47966 Y256.016428 Z2 E7132.285605 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X181.735556 Y255.191528 Z2 E7141.109 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X179.918997 Y254.541553 Z2 E7149.932394 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X178.047476 Y254.072761 Z2 E7158.755788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X176.139017 Y253.789668 Z2 E7167.579183 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X174.212 Y253.695 Z2 E7176.402577 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X172.284983 Y253.789668 Z2 E7185.225971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X170.376524 Y254.072761 Z2 E7194.049366 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X168.505003 Y254.541553 Z2 E7202.87276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X166.688444 Y255.191528 Z2 E7211.696154 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X164.94434 Y256.016428 Z2 E7220.519549 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X163.289489 Y257.008307 Z2 E7229.342943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X161.739828 Y258.157614 Z2 E7238.166338 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X160.310281 Y259.453281 Z2 E7246.989732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X159.014614 Y260.882828 Z2 E7255.813126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X157.865307 Y262.432489 Z2 E7264.636521 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X156.873428 Y264.08734 Z2 E7273.459915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X156.048528 Y265.831444 Z2 E7282.283309 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X155.398553 Y267.648003 Z2 E7291.106704 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X154.929761 Y269.519524 Z2 E7299.930098 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X154.646668 Y271.427983 Z2 E7308.753492 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X154.552 Y273.355 Z2 E7317.576887 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X154.646668 Y275.282017 Z2 E7326.400281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X154.929761 Y277.190476 Z2 E7335.223675 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X155.398553 Y279.061997 Z2 E7344.04707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X156.048528 Y280.878556 Z2 E7352.870464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X156.873428 Y282.62266 Z2 E7361.693858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X157.865307 Y284.277511 Z2 E7370.517253 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X158.334732 Y284.910457 Z2 E7374.121093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X159.014614 Y285.827172 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=end-early tail
G1 X160.310281 Y287.256719 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=end-early tail
G1 X161.739828 Y288.552386 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0015
G0 X161.739828 Y288.552386 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0016 note=intra-page lift
G0 X148.283086 Y273.181268 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0016 note=intra-page XY
G0 X148.283086 Y273.181268 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0016 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0016
G1 X149.39698 Y272.176659 Z2 E7374.464088 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X150.510875 Y271.172049 Z2 E7375.493073 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X151.2995 Y270.460797 Z2 E7376.636347 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X151.603685 Y270.145631 Z2 E7377.208049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X152.645377 Y269.066336 Z2 E7379.609015 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X153.513602 Y268.166771 Z2 E7382.134309 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X153.67107 Y267.97287 Z2 E7382.695971 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X154.616681 Y266.808474 Z2 E7386.468918 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X154.881 Y266.483 Z2 E7387.646211 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X155.671997 Y265.746607 Z2 E7390.927855 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X156.545807 Y264.933116 Z2 E7394.967035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X156.759469 Y264.713872 Z2 E7396.072782 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X157.806365 Y263.639624 Z2 E7401.903699 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X157.982959 Y263.458416 Z2 E7402.954898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X158.801578 Y262.517773 Z2 E7408.420607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X159.203112 Y262.056386 Z2 E7411.217815 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X160.216922 Y260.724516 Z2 E7418.872668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X161.035047 Y259.460291 Z2 E7425.759336 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X161.668143 Y258.261201 Z2 E7431.960505 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X162.126866 Y257.124733 Z2 E7437.565301 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X162.421875 Y256.048375 Z2 E7442.669316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X162.563825 Y255.029615 Z2 E7447.373391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X162.563373 Y254.065939 Z2 E7451.780536 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X162.431176 Y253.154838 Z2 E7455.990882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X162.177891 Y252.293797 Z2 E7460.095488 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X161.814174 Y251.480305 Z2 E7464.170728 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X161.350682 Y250.71185 Z2 E7468.274834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X160.167 Y249.3 Z2 E7476.700604 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X158.75515 Y248.116318 Z2 E7485.126374 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X157.986695 Y247.652826 Z2 E7489.23048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X157.173203 Y247.289109 Z2 E7493.30572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X156.312162 Y247.035824 Z2 E7497.410326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X155.401061 Y246.903627 Z2 E7501.620671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X154.437385 Y246.903175 Z2 E7506.027817 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X153.418625 Y247.045125 Z2 E7510.731891 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X152.342267 Y247.340134 Z2 E7515.835907 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X151.205799 Y247.798857 Z2 E7521.440703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X150.006709 Y248.431953 Z2 E7527.641872 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X148.742484 Y249.250078 Z2 E7534.52854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X147.410614 Y250.263888 Z2 E7542.183392 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X146.008584 Y251.484041 Z2 E7550.68335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X144.533884 Y252.921193 Z2 E7560.100448 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X142.984 Y254.586 Z2 E7570.502722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X141.300229 Y255.953398 Z2 E7580.422462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X139.006203 Y258.1675 Z2 E7595.003085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X136.285732 Y261.183914 Z2 E7613.579629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X133.322625 Y264.95825 Z2 E7635.524466 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X131.807523 Y267.115767 Z2 E7647.581264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X130.300689 Y269.446117 Z2 E7660.27246 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X128.825101 Y271.943753 Z2 E7673.53931 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X127.403734 Y274.603125 Z2 E7687.329473 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X126.059565 Y277.418685 Z2 E7701.597901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X124.815568 Y280.384883 Z2 E7716.30781 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X123.694721 Y283.496171 Z2 E7731.431721 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X122.72 Y286.747 Z2 E7746.952543 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X125.970829 Y285.772279 Z2 E7762.473364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X129.082117 Y284.651432 Z2 E7777.597276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X132.048315 Y283.407435 Z2 E7792.307185 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X134.863875 Y282.063266 Z2 E7806.575612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X137.523247 Y280.641899 Z2 E7820.365776 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X140.020883 Y279.166311 Z2 E7833.632626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X142.351233 Y277.659477 Z2 E7846.323821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X144.34385 Y276.260175 Z2 E7857.459113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X144.50875 Y276.144375 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=end-early tail
G1 X148.283086 Y273.181268 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0016
G0 X148.283086 Y273.181268 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0017 note=intra-page lift
G0 X141.818997 Y254.068447 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0017 note=intra-page XY
G0 X141.818997 Y254.068447 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0017 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0017
G1 X143.231313 Y253.563112 Z2 E7857.802109 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X143.635556 Y253.418472 Z2 E7858.026558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X144.603421 Y252.960706 Z2 E7858.831094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X145.37966 Y252.593572 Z2 E7859.728892 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X145.929737 Y252.263869 Z2 E7860.54607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X147.034511 Y251.601693 Z2 E7862.566114 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X147.204772 Y251.475418 Z2 E7862.947036 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X148.409584 Y250.581869 Z2 E7866.033992 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X148.584172 Y250.452386 Z2 E7866.538226 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X149.534543 Y249.59102 Z2 E7869.806939 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X150.013719 Y249.156719 Z2 E7871.645227 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X150.586757 Y248.524469 Z2 E7874.265875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X151.309386 Y247.727172 Z2 E7877.887117 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X151.561935 Y247.386649 Z2 E7879.410803 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X152.455484 Y246.181837 Z2 E7885.24172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X152.458693 Y246.177511 Z2 E7885.263896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X153.227077 Y244.895538 Z2 E7891.758628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X153.450572 Y244.52266 Z2 E7893.746754 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X154.275472 Y242.778556 Z2 E7902.570148 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X154.925447 Y240.961997 Z2 E7911.393543 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X155.394239 Y239.090476 Z2 E7920.216937 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X155.677332 Y237.182017 Z2 E7929.040331 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X155.772 Y235.255 Z2 E7937.863726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X155.677332 Y233.327983 Z2 E7946.68712 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X155.394239 Y231.419524 Z2 E7955.510514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X154.925447 Y229.548003 Z2 E7964.333909 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X154.275472 Y227.731444 Z2 E7973.157303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X153.450572 Y225.98734 Z2 E7981.980697 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X152.458693 Y224.332489 Z2 E7990.804092 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X151.309386 Y222.782828 Z2 E7999.627486 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X150.013719 Y221.353281 Z2 E8008.45088 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X148.584172 Y220.057614 Z2 E8017.274275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X147.034511 Y218.908307 Z2 E8026.097669 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X145.37966 Y217.916428 Z2 E8034.921063 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X143.635556 Y217.091528 Z2 E8043.744458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X141.818997 Y216.441553 Z2 E8052.567852 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X139.947476 Y215.972761 Z2 E8061.391247 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X138.039017 Y215.689668 Z2 E8070.214641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X136.112 Y215.595 Z2 E8079.038035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X134.184983 Y215.689668 Z2 E8087.86143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X132.276524 Y215.972761 Z2 E8096.684824 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X130.405003 Y216.441553 Z2 E8105.508218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X128.588444 Y217.091528 Z2 E8114.331613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X126.84434 Y217.916428 Z2 E8123.155007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X125.189489 Y218.908307 Z2 E8131.978401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X123.639828 Y220.057614 Z2 E8140.801796 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X122.210281 Y221.353281 Z2 E8149.62519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X120.914614 Y222.782828 Z2 E8158.448584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X119.765307 Y224.332489 Z2 E8167.271979 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X118.773428 Y225.98734 Z2 E8176.095373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X117.948528 Y227.731444 Z2 E8184.918767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X117.298553 Y229.548003 Z2 E8193.742162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X116.829761 Y231.419524 Z2 E8202.565556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X116.546668 Y233.327983 Z2 E8211.38895 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X116.452 Y235.255 Z2 E8220.212345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X116.546668 Y237.182017 Z2 E8229.035739 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X116.829761 Y239.090476 Z2 E8237.859133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X117.298553 Y240.961997 Z2 E8246.682528 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X117.948528 Y242.778556 Z2 E8255.505922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X118.773428 Y244.52266 Z2 E8264.329316 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X119.765307 Y246.177511 Z2 E8273.152711 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X120.914614 Y247.727172 Z2 E8281.976105 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X122.210281 Y249.156719 Z2 E8290.7995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X123.639828 Y250.452386 Z2 E8299.622894 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X125.189489 Y251.601693 Z2 E8308.446288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X126.84434 Y252.593572 Z2 E8317.269683 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X128.588444 Y253.418472 Z2 E8326.093077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X130.405003 Y254.068447 Z2 E8334.916471 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X132.276524 Y254.537239 Z2 E8343.739866 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X134.184983 Y254.820332 Z2 E8352.56326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X136.112 Y254.915 Z2 E8361.386654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X136.899074 Y254.876334 Z2 E8364.990494 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X138.039017 Y254.820332 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=end-early tail
G1 X139.947476 Y254.537239 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=end-early tail
G1 X141.818997 Y254.068447 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0017
G0 X141.818997 Y254.068447 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0018 note=intra-page lift
G0 X157.103834 Y244.907068 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0018 note=intra-page XY
G0 X157.103834 Y244.907068 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0018 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0018
G1 X157.865307 Y246.177511 Z2 E8365.324932 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X157.876524 Y246.192635 Z2 E8365.33349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X158.770073 Y247.397446 Z2 E8366.362475 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X159.014614 Y247.727172 Z2 E8366.763641 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X159.74627 Y248.53443 Z2 E8368.077451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X160.310281 Y249.156719 Z2 E8369.337238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X160.799418 Y249.600047 Z2 E8370.478417 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X161.739828 Y250.452386 Z2 E8373.045724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X161.925214 Y250.589877 Z2 E8373.565373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X163.130025 Y251.483426 Z2 E8377.33832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X163.289489 Y251.601693 Z2 E8377.889099 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X164.405793 Y252.27078 Z2 E8381.797256 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X164.94434 Y252.593572 Z2 E8383.867363 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X165.732731 Y252.966453 Z2 E8386.942184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X166.688444 Y253.418472 Z2 E8390.980517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X167.105344 Y253.567641 Z2 E8392.773101 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X168.505003 Y254.068447 Z2 E8399.228559 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X168.518043 Y254.071713 Z2 E8399.290009 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=prime ramp
G1 X170.376524 Y254.537239 Z2 E8408.051926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X172.284983 Y254.820332 Z2 E8416.87532 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X174.212 Y254.915 Z2 E8425.698715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X176.139017 Y254.820332 Z2 E8434.522109 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X178.047476 Y254.537239 Z2 E8443.345503 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X179.918997 Y254.068447 Z2 E8452.168898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X181.735556 Y253.418472 Z2 E8460.992292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X183.47966 Y252.593572 Z2 E8469.815686 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X185.134511 Y251.601693 Z2 E8478.639081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X186.684172 Y250.452386 Z2 E8487.462475 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X188.113719 Y249.156719 Z2 E8496.285869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X189.409386 Y247.727172 Z2 E8505.109264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X190.558693 Y246.177511 Z2 E8513.932658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X191.550572 Y244.52266 Z2 E8522.756052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X192.375472 Y242.778556 Z2 E8531.579447 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X193.025447 Y240.961997 Z2 E8540.402841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X193.494239 Y239.090476 Z2 E8549.226235 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X193.777332 Y237.182017 Z2 E8558.04963 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X193.872 Y235.255 Z2 E8566.873024 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X193.777332 Y233.327983 Z2 E8575.696418 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X193.494239 Y231.419524 Z2 E8584.519813 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X193.025447 Y229.548003 Z2 E8593.343207 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X192.375472 Y227.731444 Z2 E8602.166602 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X191.550572 Y225.98734 Z2 E8610.989996 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X190.558693 Y224.332489 Z2 E8619.81339 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X189.409386 Y222.782828 Z2 E8628.636785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X188.113719 Y221.353281 Z2 E8637.460179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X186.684172 Y220.057614 Z2 E8646.283573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X185.134511 Y218.908307 Z2 E8655.106968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X183.47966 Y217.916428 Z2 E8663.930362 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X181.735556 Y217.091528 Z2 E8672.753756 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X179.918997 Y216.441553 Z2 E8681.577151 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X178.047476 Y215.972761 Z2 E8690.400545 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X176.139017 Y215.689668 Z2 E8699.223939 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X174.212 Y215.595 Z2 E8708.047334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X172.284983 Y215.689668 Z2 E8716.870728 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X170.376524 Y215.972761 Z2 E8725.694122 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X168.505003 Y216.441553 Z2 E8734.517517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X166.688444 Y217.091528 Z2 E8743.340911 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X164.94434 Y217.916428 Z2 E8752.164305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X163.289489 Y218.908307 Z2 E8760.9877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X161.739828 Y220.057614 Z2 E8769.811094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X160.310281 Y221.353281 Z2 E8778.634488 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X159.014614 Y222.782828 Z2 E8787.457883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X157.865307 Y224.332489 Z2 E8796.281277 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X156.873428 Y225.98734 Z2 E8805.104671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X156.048528 Y227.731444 Z2 E8813.928066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X155.398553 Y229.548003 Z2 E8822.75146 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X154.929761 Y231.419524 Z2 E8831.574855 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X154.646668 Y233.327983 Z2 E8840.398249 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X154.552 Y235.255 Z2 E8849.221643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X154.646668 Y237.182017 Z2 E8858.045038 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X154.929761 Y239.090476 Z2 E8866.868432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X155.230132 Y240.289622 Z2 E8872.521876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018
G1 X155.398553 Y240.961997 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
G1 X156.048528 Y242.778556 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
G1 X156.873428 Y244.52266 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
G1 X157.103834 Y244.907068 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0018 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0018
G0 X157.103834 Y244.907068 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0019 note=intra-page lift
G0 X123.132186 Y256.553093 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0019 note=intra-page XY
G0 X123.132186 Y256.553093 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0019 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0019
G1 X122.918855 Y255.930805 Z2 E8872.587845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X122.539427 Y255.257274 Z2 E8872.833994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X122.49777 Y255.202132 Z2 E8872.864871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X122.102 Y254.67825 Z2 E8873.230854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X121.611135 Y254.188171 Z2 E8873.760265 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X121.4858 Y254.106135 Z2 E8873.893856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X120.487339 Y253.452606 Z2 E8875.202416 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X120.203722 Y253.335939 Z2 E8875.608832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X119.863531 Y253.196 Z2 E8876.134141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X118.76172 Y252.935656 Z2 E8878.009798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X118.514902 Y252.877336 Z2 E8878.483542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X117.271248 Y252.794874 Z2 E8881.096754 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X117.062 Y252.781 Z2 E8881.582982 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X115.774534 Y252.866367 Z2 E8884.869701 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X115.609098 Y252.877336 Z2 E8885.32884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X114.310653 Y253.184142 Z2 E8889.328638 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X114.260469 Y253.196 Z2 E8889.494119 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X113.636661 Y253.452606 Z2 E8891.73343 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X112.989126 Y253.876441 Z2 E8894.473565 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X112.512865 Y254.188171 Z2 E8896.605479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X112.022 Y254.67825 Z2 E8899.336931 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X111.879046 Y254.867479 Z2 E8900.304482 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X111.584573 Y255.257274 Z2 E8902.351596 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X111.205145 Y255.930805 Z2 E8905.739673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X111.127826 Y256.156345 Z2 E8906.82139 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=prime ramp
G1 X110.638531 Y257.583625 Z2 E8913.721629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X110.460469 Y258.574036 Z2 E8918.323665 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X110.337642 Y260.910663 Z2 E8929.024441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X110.402 Y262.268 Z2 E8935.238881 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X110.225023 Y263.556428 Z2 E8941.186534 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X110.180375 Y265.459984 Z2 E8949.894404 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X110.346102 Y267.88233 Z2 E8960.998337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X110.80025 Y270.727125 Z2 E8974.173089 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X111.620867 Y273.898029 Z2 E8989.152234 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X112.192991 Y275.575666 Z2 E8997.258399 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X112.886 Y277.298703 Z2 E9005.751781 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X113.709649 Y279.055097 Z2 E9014.623591 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X114.673695 Y280.832807 Z2 E9023.872041 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X115.787894 Y282.619788 Z2 E9033.502808 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X117.062 Y284.404 Z2 E9043.529389 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X118.336106 Y282.619788 Z2 E9053.555969 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X119.450305 Y280.832807 Z2 E9063.186736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X120.414351 Y279.055097 Z2 E9072.435186 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X121.238 Y277.298703 Z2 E9081.306996 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X121.931009 Y275.575666 Z2 E9089.800379 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X122.503133 Y273.898029 Z2 E9097.906543 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X123.32375 Y270.727125 Z2 E9112.885688 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X123.777898 Y267.88233 Z2 E9126.06044 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X123.943625 Y265.459984 Z2 E9137.164374 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X123.898977 Y263.556428 Z2 E9145.872244 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X123.722 Y262.268 Z2 E9151.819896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X123.759625 Y261.474481 Z2 E9155.452949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019
G1 X123.786358 Y260.910663 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
G1 X123.663531 Y258.574036 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
G1 X123.485469 Y257.583625 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
G1 X123.132186 Y256.553093 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0019 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0019
G0 X123.132186 Y256.553093 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0020 note=intra-page lift
G0 X118.548588 Y284.931416 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0020 note=intra-page XY
G0 X118.548588 Y284.931416 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0020 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0020
G1 X117.062 Y284.785 Z2 E9155.793106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X117.055811 Y284.78561 Z2 E9155.795944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X115.575412 Y284.931416 Z2 E9156.813577 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X115.56351 Y284.935027 Z2 E9156.82493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X114.145952 Y285.365038 Z2 E9158.514362 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X114.129499 Y285.373833 Z2 E9158.539905 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X112.828555 Y286.069202 Z2 E9160.895462 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X112.809326 Y286.084982 Z2 E9160.940871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X111.673846 Y287.016846 Z2 E9163.956875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X111.654121 Y287.040882 Z2 E9164.027828 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X110.726202 Y288.171555 Z2 E9167.698602 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X110.708612 Y288.204462 Z2 E9167.800774 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X110.022038 Y289.488952 Z2 E9172.120643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X110.009401 Y289.530609 Z2 E9172.259711 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X109.588416 Y290.918412 Z2 E9177.222999 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X109.58354 Y290.967922 Z2 E9177.404638 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X109.442 Y292.405 Z2 E9183.005668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X109.447486 Y292.4607 Z2 E9183.235556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X109.588416 Y293.891588 Z2 E9189.468651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X109.606468 Y293.951098 Z2 E9189.752463 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=prime ramp
G1 X110.022038 Y295.321048 Z2 E9196.299525 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X110.726202 Y296.638445 Z2 E9203.130987 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X111.673846 Y297.793154 Z2 E9209.96245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X112.828555 Y298.740798 Z2 E9216.793913 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X114.145952 Y299.444962 Z2 E9223.625375 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X115.575412 Y299.878584 Z2 E9230.456838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X117.062 Y300.025 Z2 E9237.288301 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X118.548588 Y299.878584 Z2 E9244.119763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X119.978048 Y299.444962 Z2 E9250.951226 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X121.295445 Y298.740798 Z2 E9257.782689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X122.450154 Y297.793154 Z2 E9264.614152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X123.397798 Y296.638445 Z2 E9271.445614 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X124.101962 Y295.321048 Z2 E9278.277077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X124.535584 Y293.891588 Z2 E9285.10854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X124.682 Y292.405 Z2 E9291.940002 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X124.535584 Y290.918412 Z2 E9298.771465 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X124.101962 Y289.488952 Z2 E9305.602928 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X123.397798 Y288.171555 Z2 E9312.43439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X122.779186 Y287.417773 Z2 E9316.893898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020
G1 X122.450154 Y287.016846 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=end-early tail
G1 X121.295445 Y286.069202 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=end-early tail
G1 X119.978048 Y285.365038 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=end-early tail
G1 X118.548588 Y284.931416 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0020 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0020
; CLAYLINE_MARKER page=0 layer=1 text=layer 1 page_id=page-0-rings-grid-1 page_name=rings-grid z_mode=calibrated
G0 X118.548588 Y284.931416 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0020 note=vertical layer transition
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0020
G1 X119.978048 Y285.365038 Z4 E9317.203132 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X119.983532 Y285.367969 Z4 E9317.205712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X121.295445 Y286.069202 Z4 E9318.130833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X121.30506 Y286.077092 Z4 E9318.141153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X122.450154 Y287.016846 Z4 E9319.677001 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X122.461989 Y287.031268 Z4 E9319.700222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X123.397798 Y288.171555 Z4 E9321.841637 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X123.409524 Y288.193493 Z4 E9321.882919 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.101962 Y289.488952 Z4 E9324.62474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.110988 Y289.518707 Z4 E9324.689242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.535584 Y290.918412 Z4 E9328.02631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.539241 Y290.955545 Z4 E9328.119194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.682 Y292.405 Z4 E9332.046348 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.677733 Y292.448322 Z4 E9332.172773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.535584 Y293.891588 Z4 E9336.684852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.521142 Y293.939196 Z4 E9336.849979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.101962 Y295.321048 Z4 E9341.941825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X124.075578 Y295.370408 Z4 E9342.150813 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X123.397798 Y296.638445 Z4 E9347.817264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X123.358347 Y296.686517 Z4 E9348.075275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=prime ramp
G1 X122.450154 Y297.793154 Z4 E9354.027149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X121.295445 Y298.740798 Z4 E9360.237569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X119.978048 Y299.444962 Z4 E9366.44799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X118.548588 Y299.878584 Z4 E9372.658411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X117.062 Y300.025 Z4 E9378.868831 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X115.575412 Y299.878584 Z4 E9385.079252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X114.145952 Y299.444962 Z4 E9391.289672 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X112.828555 Y298.740798 Z4 E9397.500093 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X111.673846 Y297.793154 Z4 E9403.710514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X110.726202 Y296.638445 Z4 E9409.920934 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X110.022038 Y295.321048 Z4 E9416.131355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X109.588416 Y293.891588 Z4 E9422.341776 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X109.442 Y292.405 Z4 E9428.552196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X109.588416 Y290.918412 Z4 E9434.762617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X110.022038 Y289.488952 Z4 E9440.973038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X110.726202 Y288.171555 Z4 E9447.183458 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X111.673846 Y287.016846 Z4 E9453.393879 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X112.828555 Y286.069202 Z4 E9459.604299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X113.688538 Y285.609531 Z4 E9463.658398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020
G1 X114.145952 Y285.365038 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=end-early tail
G1 X115.575412 Y284.931416 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=end-early tail
G1 X117.062 Y284.785 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=end-early tail
G1 X118.548588 Y284.931416 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0020 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0020
G0 X118.548588 Y284.931416 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0019 note=intra-page lift
G0 X123.132186 Y256.553093 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0019 note=intra-page XY
G0 X123.132186 Y256.553093 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0019 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0019
G1 X123.485469 Y257.583625 Z4 E9463.822869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.558123 Y257.98774 Z4 E9463.970211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.663531 Y258.574036 Z4 E9464.26705 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.711001 Y259.477094 Z4 E9464.905653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.786358 Y260.910663 Z4 E9466.38491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.783305 Y260.975042 Z4 E9466.464721 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.722 Y262.268 Z4 E9468.311379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.749977 Y262.471677 Z4 E9468.647418 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.898977 Y263.556428 Z4 E9470.63445 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.908475 Y263.96138 Z4 E9471.453742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.943625 Y265.459984 Z4 E9474.881239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.943558 Y265.460966 Z4 E9474.883693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.841174 Y266.957468 Z4 E9478.937272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.777898 Y267.88233 Z4 E9481.754252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.687571 Y268.448141 Z4 E9483.614479 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.451103 Y269.929385 Z4 E9488.915313 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.32375 Y270.727125 Z4 E9492.028509 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X123.150335 Y271.397207 Z4 E9494.839774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=prime ramp
G1 X122.503133 Y273.898029 Z4 E9505.57952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X121.931009 Y275.575666 Z4 E9512.94876 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X121.238 Y277.298703 Z4 E9520.670017 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X120.414351 Y279.055097 Z4 E9528.735299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X119.450305 Y280.832807 Z4 E9537.142981 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X118.336106 Y282.619788 Z4 E9545.898223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X117.062 Y284.404 Z4 E9555.013297 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X115.787894 Y282.619788 Z4 E9564.12837 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X114.673695 Y280.832807 Z4 E9572.883612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X113.709649 Y279.055097 Z4 E9581.291294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X112.886 Y277.298703 Z4 E9589.356576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X112.192991 Y275.575666 Z4 E9597.077833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X111.620867 Y273.898029 Z4 E9604.447073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X110.80025 Y270.727125 Z4 E9618.064478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X110.346102 Y267.88233 Z4 E9630.041525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X110.180375 Y265.459984 Z4 E9640.13601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X110.225023 Y263.556428 Z4 E9648.052256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X110.402 Y262.268 Z4 E9653.459213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X110.337642 Y260.910663 Z4 E9659.108704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X110.460469 Y258.574036 Z4 E9668.836682 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X110.638531 Y257.583625 Z4 E9673.020351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X111.205145 Y255.930805 Z4 E9680.284553 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X111.584573 Y255.257274 Z4 E9683.498528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X112.022 Y254.67825 Z4 E9686.515556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X112.512865 Y254.188171 Z4 E9689.399344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X113.636661 Y253.452606 Z4 E9694.983389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X114.260469 Y253.196 Z4 E9697.787736 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X115.609098 Y252.877336 Z4 E9703.549081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X117.062 Y252.781 Z4 E9709.602811 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X118.514902 Y252.877336 Z4 E9715.656541 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X119.734922 Y253.165611 Z4 E9720.868465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019
G1 X119.863531 Y253.196 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X120.487339 Y253.452606 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X121.611135 Y254.188171 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X122.102 Y254.67825 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X122.539427 Y255.257274 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X122.918855 Y255.930805 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
G1 X123.132186 Y256.553093 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0019 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0019
G0 X123.132186 Y256.553093 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0018 note=intra-page lift
G0 X157.103834 Y244.907068 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0018 note=intra-page XY
G0 X157.103834 Y244.907068 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0018 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0018
G1 X156.873428 Y244.52266 Z4 E9720.8963 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X156.423713 Y243.571817 Z4 E9721.180278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X156.048528 Y242.778556 Z4 E9721.651818 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X155.838818 Y242.192456 Z4 E9722.11572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X155.398553 Y240.961997 Z4 E9723.439054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X155.351622 Y240.774637 Z4 E9723.674788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.987152 Y239.319591 Z4 E9725.857485 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.929761 Y239.090476 Z4 E9726.258007 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.744322 Y237.840348 Z4 E9728.663809 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.646668 Y237.182017 Z4 E9730.108677 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.605723 Y236.348556 Z4 E9732.09376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.552 Y235.255 Z4 E9734.991065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.571879 Y234.850363 Z4 E9736.147339 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.64548 Y233.35217 Z4 E9740.824546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.646668 Y233.327983 Z4 E9740.90517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.863211 Y231.868172 Z4 E9746.12538 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X154.929761 Y231.419524 Z4 E9747.850992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X155.184026 Y230.404442 Z4 E9752.049841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=prime ramp
G1 X155.398553 Y229.548003 Z4 E9755.720504 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X156.048528 Y227.731444 Z4 E9763.741772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X156.873428 Y225.98734 Z4 E9771.76304 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X157.865307 Y224.332489 Z4 E9779.784307 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X159.014614 Y222.782828 Z4 E9787.805575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X160.310281 Y221.353281 Z4 E9795.826842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X161.739828 Y220.057614 Z4 E9803.84811 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X163.289489 Y218.908307 Z4 E9811.869378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X164.94434 Y217.916428 Z4 E9819.890645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X166.688444 Y217.091528 Z4 E9827.911913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X168.505003 Y216.441553 Z4 E9835.93318 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X170.376524 Y215.972761 Z4 E9843.954448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X172.284983 Y215.689668 Z4 E9851.975716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X174.212 Y215.595 Z4 E9859.996983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X176.139017 Y215.689668 Z4 E9868.018251 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X178.047476 Y215.972761 Z4 E9876.039518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X179.918997 Y216.441553 Z4 E9884.060786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X181.735556 Y217.091528 Z4 E9892.082053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X183.47966 Y217.916428 Z4 E9900.103321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X185.134511 Y218.908307 Z4 E9908.124589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X186.684172 Y220.057614 Z4 E9916.145856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X188.113719 Y221.353281 Z4 E9924.167124 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X189.409386 Y222.782828 Z4 E9932.188391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X190.558693 Y224.332489 Z4 E9940.209659 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X191.550572 Y225.98734 Z4 E9948.230927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X192.375472 Y227.731444 Z4 E9956.252194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X193.025447 Y229.548003 Z4 E9964.273462 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X193.494239 Y231.419524 Z4 E9972.294729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X193.777332 Y233.327983 Z4 E9980.315997 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X193.872 Y235.255 Z4 E9988.337264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X193.777332 Y237.182017 Z4 E9996.358532 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X193.494239 Y239.090476 Z4 E10004.3798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X193.025447 Y240.961997 Z4 E10012.401067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X192.375472 Y242.778556 Z4 E10020.422335 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X191.550572 Y244.52266 Z4 E10028.443602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X190.558693 Y246.177511 Z4 E10036.46487 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X189.409386 Y247.727172 Z4 E10044.486138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X188.113719 Y249.156719 Z4 E10052.507405 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X186.684172 Y250.452386 Z4 E10060.528673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X185.134511 Y251.601693 Z4 E10068.54994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X183.47966 Y252.593572 Z4 E10076.571208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X181.735556 Y253.418472 Z4 E10084.592476 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X179.918997 Y254.068447 Z4 E10092.613743 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X178.047476 Y254.537239 Z4 E10100.635011 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X176.139017 Y254.820332 Z4 E10108.656278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X174.212 Y254.915 Z4 E10116.677546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X172.284983 Y254.820332 Z4 E10124.698813 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X170.376524 Y254.537239 Z4 E10132.720081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X168.505003 Y254.068447 Z4 E10140.741349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X166.688444 Y253.418472 Z4 E10148.762616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X164.94434 Y252.593572 Z4 E10156.783884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X163.289489 Y251.601693 Z4 E10164.805151 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X161.739828 Y250.452386 Z4 E10172.826419 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X160.310281 Y249.156719 Z4 E10180.847687 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X160.08205 Y248.904905 Z4 E10182.260629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018
G1 X159.014614 Y247.727172 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=end-early tail
G1 X157.865307 Y246.177511 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=end-early tail
G1 X157.103834 Y244.907068 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0018 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0018
G0 X157.103834 Y244.907068 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0017 note=intra-page lift
G0 X141.818997 Y254.068447 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0017 note=intra-page XY
G0 X141.818997 Y254.068447 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0017 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0017
G1 X140.36395 Y254.432917 Z4 E10182.572443 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X139.947476 Y254.537239 Z4 E10182.776488 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X138.888405 Y254.694337 Z4 E10183.507884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X138.039017 Y254.820332 Z4 E10184.324064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X137.398471 Y254.8518 Z4 E10185.066953 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X136.112 Y254.915 Z4 E10186.903357 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X135.900278 Y254.904599 Z4 E10187.249649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X134.402085 Y254.830997 Z4 E10190.055973 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X134.184983 Y254.820332 Z4 E10190.514368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X132.916229 Y254.63213 Z4 E10193.485925 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X132.276524 Y254.537239 Z4 E10195.157096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X131.448801 Y254.329905 Z4 E10197.539504 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X130.405003 Y254.068447 Z4 E10200.831541 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X130.005832 Y253.925621 Z4 E10202.21671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X128.593516 Y253.420286 Z4 E10207.517544 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X128.588444 Y253.418472 Z4 E10207.537704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X127.237329 Y252.779442 Z4 E10213.442006 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=prime ramp
G1 X126.84434 Y252.593572 Z4 E10215.249393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X125.189489 Y251.601693 Z4 E10223.270661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X123.639828 Y250.452386 Z4 E10231.291928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X122.210281 Y249.156719 Z4 E10239.313196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X120.914614 Y247.727172 Z4 E10247.334464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X119.765307 Y246.177511 Z4 E10255.355731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X118.773428 Y244.52266 Z4 E10263.376999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X117.948528 Y242.778556 Z4 E10271.398266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X117.298553 Y240.961997 Z4 E10279.419534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X116.829761 Y239.090476 Z4 E10287.440801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X116.546668 Y237.182017 Z4 E10295.462069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X116.452 Y235.255 Z4 E10303.483337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X116.546668 Y233.327983 Z4 E10311.504604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X116.829761 Y231.419524 Z4 E10319.525872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X117.298553 Y229.548003 Z4 E10327.547139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X117.948528 Y227.731444 Z4 E10335.568407 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X118.773428 Y225.98734 Z4 E10343.589675 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X119.765307 Y224.332489 Z4 E10351.610942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X120.914614 Y222.782828 Z4 E10359.63221 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X122.210281 Y221.353281 Z4 E10367.653477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X123.639828 Y220.057614 Z4 E10375.674745 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X125.189489 Y218.908307 Z4 E10383.696013 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X126.84434 Y217.916428 Z4 E10391.71728 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X128.588444 Y217.091528 Z4 E10399.738548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X130.405003 Y216.441553 Z4 E10407.759815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X132.276524 Y215.972761 Z4 E10415.781083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X134.184983 Y215.689668 Z4 E10423.80235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X136.112 Y215.595 Z4 E10431.823618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X138.039017 Y215.689668 Z4 E10439.844886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X139.947476 Y215.972761 Z4 E10447.866153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X141.818997 Y216.441553 Z4 E10455.887421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X143.635556 Y217.091528 Z4 E10463.908688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X145.37966 Y217.916428 Z4 E10471.929956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X147.034511 Y218.908307 Z4 E10479.951224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X148.584172 Y220.057614 Z4 E10487.972491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X150.013719 Y221.353281 Z4 E10495.993759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X151.309386 Y222.782828 Z4 E10504.015026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X152.458693 Y224.332489 Z4 E10512.036294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X153.450572 Y225.98734 Z4 E10520.057562 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X154.275472 Y227.731444 Z4 E10528.078829 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X154.925447 Y229.548003 Z4 E10536.100097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X155.394239 Y231.419524 Z4 E10544.121364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X155.677332 Y233.327983 Z4 E10552.142632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X155.772 Y235.255 Z4 E10560.163899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X155.677332 Y237.182017 Z4 E10568.185167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X155.394239 Y239.090476 Z4 E10576.206435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X154.925447 Y240.961997 Z4 E10584.227702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X154.275472 Y242.778556 Z4 E10592.24897 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X153.450572 Y244.52266 Z4 E10600.270237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X152.458693 Y246.177511 Z4 E10608.291505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X151.309386 Y247.727172 Z4 E10616.312773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X150.013719 Y249.156719 Z4 E10624.33404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X148.584172 Y250.452386 Z4 E10632.355308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X147.034511 Y251.601693 Z4 E10640.376575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X146.358601 Y252.006817 Z4 E10643.652794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X145.37966 Y252.593572 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=end-early tail
G1 X143.635556 Y253.418472 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=end-early tail
G1 X141.818997 Y254.068447 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0017
G0 X141.818997 Y254.068447 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0016 note=intra-page lift
G0 X148.283086 Y273.181268 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0016 note=intra-page XY
G0 X148.283086 Y273.181268 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0016 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0016
G1 X147.103238 Y274.107528 Z4 E10643.964607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X145.923389 Y275.033788 Z4 E10644.900049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X144.743541 Y275.960048 Z4 E10646.459118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X144.50875 Y276.144375 Z4 E10646.843773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X143.525482 Y276.834869 Z4 E10648.641814 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X142.351233 Y277.659477 Z4 E10651.313326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X142.296537 Y277.694845 Z4 E10651.448138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X141.036925 Y278.509325 Z4 E10654.878089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X140.020883 Y279.166311 Z4 E10658.099198 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X139.771156 Y279.313848 Z4 E10658.931668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X138.479701 Y280.076831 Z4 E10663.608875 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X137.523247 Y280.641899 Z4 E10667.47478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X137.180089 Y280.825308 Z4 E10668.909709 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X135.857187 Y281.532366 Z4 E10674.83417 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=prime ramp
G1 X134.863875 Y282.063266 Z4 E10679.51673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X132.048315 Y283.407435 Z4 E10692.488028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X129.082117 Y284.651432 Z4 E10705.860672 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X125.970829 Y285.772279 Z4 E10719.609682 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X122.72 Y286.747 Z4 E10733.71952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X123.694721 Y283.496171 Z4 E10747.829358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X124.815568 Y280.384883 Z4 E10761.578369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X126.059565 Y277.418685 Z4 E10774.951013 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X127.403734 Y274.603125 Z4 E10787.922311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X128.825101 Y271.943753 Z4 E10800.458823 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X130.300689 Y269.446117 Z4 E10812.519596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X131.807523 Y267.115767 Z4 E10824.057046 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X133.322625 Y264.95825 Z4 E10835.017772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X136.285732 Y261.183914 Z4 E10854.967624 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X139.006203 Y258.1675 Z4 E10871.855391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X141.300229 Y255.953398 Z4 E10885.110503 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X142.984 Y254.586 Z4 E10894.128448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X144.533884 Y252.921193 Z4 E10903.585061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X146.008584 Y251.484041 Z4 E10912.14606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X147.410614 Y250.263888 Z4 E10919.873293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X148.742484 Y249.250078 Z4 E10926.83225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X150.006709 Y248.431953 Z4 E10933.092857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X151.205799 Y247.798857 Z4 E10938.730284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X152.342267 Y247.340134 Z4 E10943.825553 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X153.418625 Y247.045125 Z4 E10948.465567 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X154.437385 Y246.903175 Z4 E10952.741998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X155.401061 Y246.903627 Z4 E10956.748494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X156.312162 Y247.035824 Z4 E10960.576081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X157.173203 Y247.289109 Z4 E10964.307541 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X157.986695 Y247.652826 Z4 E10968.012305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X158.75515 Y248.116318 Z4 E10971.74331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X160.167 Y249.3 Z4 E10979.403101 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X161.350682 Y250.71185 Z4 E10987.062892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X161.814174 Y251.480305 Z4 E10990.793898 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X162.177891 Y252.293797 Z4 E10994.498661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X162.431176 Y253.154838 Z4 E10998.230121 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X162.563373 Y254.065939 Z4 E11002.057708 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X162.563825 Y255.029615 Z4 E11006.064204 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X162.421875 Y256.048375 Z4 E11010.340635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X162.126866 Y257.124733 Z4 E11014.980649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X161.668143 Y258.261201 Z4 E11020.075918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X161.035047 Y259.460291 Z4 E11025.713345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X160.216922 Y260.724516 Z4 E11031.973952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X159.203112 Y262.056386 Z4 E11038.932909 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X157.982959 Y263.458416 Z4 E11046.660143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X156.545807 Y264.933116 Z4 E11055.221141 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X154.881 Y266.483 Z4 E11064.677754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X153.513602 Y268.166771 Z4 E11073.695699 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X151.950916 Y269.785866 Z4 E11083.050994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X151.2995 Y270.460797 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=end-early tail
G1 X148.283086 Y273.181268 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0016
G0 X148.283086 Y273.181268 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0015 note=intra-page lift
G0 X161.739828 Y288.552386 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0015 note=intra-page XY
G0 X161.739828 Y288.552386 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0015 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0015
G1 X160.628401 Y287.545047 Z4 E11083.362808 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X160.310281 Y287.256719 Z4 E11083.566853 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X159.59127 Y286.463413 Z4 E11084.298249 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X159.014614 Y285.827172 Z4 E11085.114429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X158.632582 Y285.31206 Z4 E11085.857318 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X157.865307 Y284.277511 Z4 E11087.693722 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X157.756329 Y284.095692 Z4 E11088.040014 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X156.985175 Y282.809099 Z4 E11090.846338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X156.873428 Y282.62266 Z4 E11091.304733 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X156.32503 Y281.46317 Z4 E11094.27629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X156.048528 Y280.878556 Z4 E11095.947461 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X155.761062 Y280.075141 Z4 E11098.329869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X155.398553 Y279.061997 Z4 E11101.621906 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X155.295541 Y278.650748 Z4 E11103.007075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X154.93107 Y277.195701 Z4 E11108.307909 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X154.929761 Y277.190476 Z4 E11108.328069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X154.710456 Y275.712039 Z4 E11114.232371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=prime ramp
G1 X154.646668 Y275.282017 Z4 E11116.039758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X154.552 Y273.355 Z4 E11124.061026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X154.646668 Y271.427983 Z4 E11132.082293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X154.929761 Y269.519524 Z4 E11140.103561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X155.398553 Y267.648003 Z4 E11148.124829 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X156.048528 Y265.831444 Z4 E11156.146096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X156.873428 Y264.08734 Z4 E11164.167364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X157.865307 Y262.432489 Z4 E11172.188631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X159.014614 Y260.882828 Z4 E11180.209899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X160.310281 Y259.453281 Z4 E11188.231167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X161.739828 Y258.157614 Z4 E11196.252434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X163.289489 Y257.008307 Z4 E11204.273702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X164.94434 Y256.016428 Z4 E11212.294969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X166.688444 Y255.191528 Z4 E11220.316237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X168.505003 Y254.541553 Z4 E11228.337504 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X170.376524 Y254.072761 Z4 E11236.358772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X172.284983 Y253.789668 Z4 E11244.38004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X174.212 Y253.695 Z4 E11252.401307 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X176.139017 Y253.789668 Z4 E11260.422575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X178.047476 Y254.072761 Z4 E11268.443842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X179.918997 Y254.541553 Z4 E11276.46511 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X181.735556 Y255.191528 Z4 E11284.486378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X183.47966 Y256.016428 Z4 E11292.507645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X185.134511 Y257.008307 Z4 E11300.528913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X186.684172 Y258.157614 Z4 E11308.55018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X188.113719 Y259.453281 Z4 E11316.571448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X189.409386 Y260.882828 Z4 E11324.592716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X190.558693 Y262.432489 Z4 E11332.613983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X191.550572 Y264.08734 Z4 E11340.635251 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X192.375472 Y265.831444 Z4 E11348.656518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X193.025447 Y267.648003 Z4 E11356.677786 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X193.494239 Y269.519524 Z4 E11364.699053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X193.777332 Y271.427983 Z4 E11372.720321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X193.872 Y273.355 Z4 E11380.741589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X193.777332 Y275.282017 Z4 E11388.762856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X193.494239 Y277.190476 Z4 E11396.784124 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X193.025447 Y279.061997 Z4 E11404.805391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X192.375472 Y280.878556 Z4 E11412.826659 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X191.550572 Y282.62266 Z4 E11420.847927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X190.558693 Y284.277511 Z4 E11428.869194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X189.409386 Y285.827172 Z4 E11436.890462 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X188.113719 Y287.256719 Z4 E11444.911729 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X186.684172 Y288.552386 Z4 E11452.932997 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X185.134511 Y289.701693 Z4 E11460.954265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X183.47966 Y290.693572 Z4 E11468.975532 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X181.735556 Y291.518472 Z4 E11476.9968 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X179.918997 Y292.168447 Z4 E11485.018067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X178.047476 Y292.637239 Z4 E11493.039335 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X176.139017 Y292.920332 Z4 E11501.060602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X174.212 Y293.015 Z4 E11509.08187 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X172.284983 Y292.920332 Z4 E11517.103138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X170.376524 Y292.637239 Z4 E11525.124405 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X168.505003 Y292.168447 Z4 E11533.145673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X166.688444 Y291.518472 Z4 E11541.16694 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X165.976079 Y291.181548 Z4 E11544.443159 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X164.94434 Y290.693572 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=end-early tail
G1 X163.289489 Y289.701693 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=end-early tail
G1 X161.739828 Y288.552386 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0015
G0 X161.739828 Y288.552386 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0014 note=intra-page lift
G0 X152.913907 Y298.475186 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0014 note=intra-page XY
G0 X152.913907 Y298.475186 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0014 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0014
G1 X151.883375 Y298.828469 Z4 E11544.607631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X151.47926 Y298.901123 Z4 E11544.754973 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X150.892964 Y299.006531 Z4 E11545.051811 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X149.989906 Y299.054001 Z4 E11545.690414 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X148.556337 Y299.129358 Z4 E11547.169671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X148.491958 Y299.126305 Z4 E11547.249483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X147.199 Y299.065 Z4 E11549.09614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X146.995323 Y299.092977 Z4 E11549.432179 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X145.910572 Y299.241977 Z4 E11551.419211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X145.50562 Y299.251475 Z4 E11552.238503 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X144.007016 Y299.286625 Z4 E11555.666001 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X144.006034 Y299.286558 Z4 E11555.668454 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X142.509532 Y299.184174 Z4 E11559.722033 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X141.58467 Y299.120898 Z4 E11562.539013 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X141.018859 Y299.030571 Z4 E11564.39924 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X139.537615 Y298.794103 Z4 E11569.700074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X138.739875 Y298.66675 Z4 E11572.81327 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X138.069793 Y298.493335 Z4 E11575.624535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X135.568971 Y297.846133 Z4 E11586.364281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X133.891334 Y297.274009 Z4 E11593.733522 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X132.168297 Y296.581 Z4 E11601.454778 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X130.411903 Y295.757351 Z4 E11609.52006 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X128.634193 Y294.793305 Z4 E11617.927742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X126.847212 Y293.679106 Z4 E11626.682984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X125.063 Y292.405 Z4 E11635.798058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X126.847212 Y291.130894 Z4 E11644.913131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X128.634193 Y290.016695 Z4 E11653.668374 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X130.411903 Y289.052649 Z4 E11662.076056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X132.168297 Y288.229 Z4 E11670.141338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X133.891334 Y287.535991 Z4 E11677.862594 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X135.568971 Y286.963867 Z4 E11685.231835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X138.739875 Y286.14325 Z4 E11698.849239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X141.58467 Y285.689102 Z4 E11710.826286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X144.007016 Y285.523375 Z4 E11720.920772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X145.910572 Y285.568023 Z4 E11728.837017 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X147.199 Y285.745 Z4 E11734.243974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X148.556337 Y285.680642 Z4 E11739.893465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X150.892964 Y285.803469 Z4 E11749.621443 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X151.883375 Y285.981531 Z4 E11753.805113 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X153.536195 Y286.548145 Z4 E11761.069314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X154.209726 Y286.927573 Z4 E11764.283289 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X154.78875 Y287.365 Z4 E11767.300317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X155.278829 Y287.855865 Z4 E11770.184105 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X156.014394 Y288.979661 Z4 E11775.76815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X156.271 Y289.603469 Z4 E11778.572498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X156.589664 Y290.952098 Z4 E11784.333842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X156.686 Y292.405 Z4 E11790.387572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X156.589664 Y293.857902 Z4 E11796.441302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X156.301389 Y295.077922 Z4 E11801.653226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X156.271 Y295.206531 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X156.014394 Y295.830339 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X155.278829 Y296.954135 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X154.78875 Y297.445 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X154.209726 Y297.882427 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X153.536195 Y298.261855 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X152.913907 Y298.475186 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0014
G0 X152.913907 Y298.475186 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0013 note=intra-page lift
G0 X164.559932 Y332.446834 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0013 note=intra-page XY
G0 X164.559932 Y332.446834 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0013 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0013
G1 X164.94434 Y332.216428 Z4 E11801.681061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X165.895183 Y331.766713 Z4 E11801.965039 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X166.688444 Y331.391528 Z4 E11802.436579 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X167.274544 Y331.181818 Z4 E11802.900481 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X168.505003 Y330.741553 Z4 E11804.223815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X168.692363 Y330.694622 Z4 E11804.45955 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X170.147409 Y330.330152 Z4 E11806.642246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X170.376524 Y330.272761 Z4 E11807.042768 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X171.626652 Y330.087322 Z4 E11809.44857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X172.284983 Y329.989668 Z4 E11810.893438 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X173.118444 Y329.948723 Z4 E11812.878521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X174.212 Y329.895 Z4 E11815.775826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X174.616637 Y329.914879 Z4 E11816.9321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X176.11483 Y329.98848 Z4 E11821.609307 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X176.139017 Y329.989668 Z4 E11821.689931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X177.598828 Y330.206211 Z4 E11826.910141 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X178.047476 Y330.272761 Z4 E11828.635753 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X179.062558 Y330.527026 Z4 E11832.834602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=prime ramp
G1 X179.918997 Y330.741553 Z4 E11836.505266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X181.735556 Y331.391528 Z4 E11844.526533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X183.47966 Y332.216428 Z4 E11852.547801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X185.134511 Y333.208307 Z4 E11860.569068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X186.684172 Y334.357614 Z4 E11868.590336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X188.113719 Y335.653281 Z4 E11876.611604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X189.409386 Y337.082828 Z4 E11884.632871 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X190.558693 Y338.632489 Z4 E11892.654139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X191.550572 Y340.28734 Z4 E11900.675406 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X192.375472 Y342.031444 Z4 E11908.696674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X193.025447 Y343.848003 Z4 E11916.717942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X193.494239 Y345.719524 Z4 E11924.739209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X193.777332 Y347.627983 Z4 E11932.760477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X193.872 Y349.555 Z4 E11940.781744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X193.777332 Y351.482017 Z4 E11948.803012 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X193.494239 Y353.390476 Z4 E11956.824279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X193.025447 Y355.261997 Z4 E11964.845547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X192.375472 Y357.078556 Z4 E11972.866815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X191.550572 Y358.82266 Z4 E11980.888082 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X190.558693 Y360.477511 Z4 E11988.90935 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X189.409386 Y362.027172 Z4 E11996.930617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X188.113719 Y363.456719 Z4 E12004.951885 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X186.684172 Y364.752386 Z4 E12012.973153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X185.134511 Y365.901693 Z4 E12020.99442 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X183.47966 Y366.893572 Z4 E12029.015688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X181.735556 Y367.718472 Z4 E12037.036955 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X179.918997 Y368.368447 Z4 E12045.058223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X178.047476 Y368.837239 Z4 E12053.07949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X176.139017 Y369.120332 Z4 E12061.100758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X174.212 Y369.215 Z4 E12069.122026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X172.284983 Y369.120332 Z4 E12077.143293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X170.376524 Y368.837239 Z4 E12085.164561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X168.505003 Y368.368447 Z4 E12093.185828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X166.688444 Y367.718472 Z4 E12101.207096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X164.94434 Y366.893572 Z4 E12109.228364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X163.289489 Y365.901693 Z4 E12117.249631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X161.739828 Y364.752386 Z4 E12125.270899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X160.310281 Y363.456719 Z4 E12133.292166 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X159.014614 Y362.027172 Z4 E12141.313434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X157.865307 Y360.477511 Z4 E12149.334702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X156.873428 Y358.82266 Z4 E12157.355969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X156.048528 Y357.078556 Z4 E12165.377237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X155.398553 Y355.261997 Z4 E12173.398504 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X154.929761 Y353.390476 Z4 E12181.419772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X154.646668 Y351.482017 Z4 E12189.441039 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X154.552 Y349.555 Z4 E12197.462307 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X154.646668 Y347.627983 Z4 E12205.483575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X154.929761 Y345.719524 Z4 E12213.504842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X155.398553 Y343.848003 Z4 E12221.52611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X156.048528 Y342.031444 Z4 E12229.547377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X156.873428 Y340.28734 Z4 E12237.568645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X157.865307 Y338.632489 Z4 E12245.589913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X159.014614 Y337.082828 Z4 E12253.61118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X160.310281 Y335.653281 Z4 E12261.632448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X160.562095 Y335.42505 Z4 E12263.04539 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X161.739828 Y334.357614 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
G1 X163.289489 Y333.208307 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
G1 X164.559932 Y332.446834 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0013
G0 X164.559932 Y332.446834 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0012 note=intra-page lift
G0 X155.398553 Y317.161997 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0012 note=intra-page XY
G0 X155.398553 Y317.161997 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0012 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0012
G1 X155.034083 Y315.70695 Z4 E12263.357204 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.929761 Y315.290476 Z4 E12263.561249 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.772663 Y314.231405 Z4 E12264.292645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.646668 Y313.382017 Z4 E12265.108825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.6152 Y312.741471 Z4 E12265.851714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.552 Y311.455 Z4 E12267.688118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.562401 Y311.243278 Z4 E12268.034411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.636003 Y309.745085 Z4 E12270.840734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.646668 Y309.527983 Z4 E12271.299129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.83487 Y308.259229 Z4 E12274.270686 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X154.929761 Y307.619524 Z4 E12275.941857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X155.137095 Y306.791801 Z4 E12278.324265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X155.398553 Y305.748003 Z4 E12281.616302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X155.541379 Y305.348832 Z4 E12283.001471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X156.046714 Y303.936516 Z4 E12288.302305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X156.048528 Y303.931444 Z4 E12288.322465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X156.687558 Y302.580329 Z4 E12294.226767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=prime ramp
G1 X156.873428 Y302.18734 Z4 E12296.034154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X157.865307 Y300.532489 Z4 E12304.055422 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X159.014614 Y298.982828 Z4 E12312.07669 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X160.310281 Y297.553281 Z4 E12320.097957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X161.739828 Y296.257614 Z4 E12328.119225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X163.289489 Y295.108307 Z4 E12336.140492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X164.94434 Y294.116428 Z4 E12344.16176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X166.688444 Y293.291528 Z4 E12352.183027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X168.505003 Y292.641553 Z4 E12360.204295 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X170.376524 Y292.172761 Z4 E12368.225563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X172.284983 Y291.889668 Z4 E12376.24683 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X174.212 Y291.795 Z4 E12384.268098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X176.139017 Y291.889668 Z4 E12392.289365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X178.047476 Y292.172761 Z4 E12400.310633 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X179.918997 Y292.641553 Z4 E12408.331901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X181.735556 Y293.291528 Z4 E12416.353168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X183.47966 Y294.116428 Z4 E12424.374436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X185.134511 Y295.108307 Z4 E12432.395703 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X186.684172 Y296.257614 Z4 E12440.416971 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X188.113719 Y297.553281 Z4 E12448.438239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X189.409386 Y298.982828 Z4 E12456.459506 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X190.558693 Y300.532489 Z4 E12464.480774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X191.550572 Y302.18734 Z4 E12472.502041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X192.375472 Y303.931444 Z4 E12480.523309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X193.025447 Y305.748003 Z4 E12488.544576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X193.494239 Y307.619524 Z4 E12496.565844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X193.777332 Y309.527983 Z4 E12504.587112 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X193.872 Y311.455 Z4 E12512.608379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X193.777332 Y313.382017 Z4 E12520.629647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X193.494239 Y315.290476 Z4 E12528.650914 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X193.025447 Y317.161997 Z4 E12536.672182 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X192.375472 Y318.978556 Z4 E12544.69345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X191.550572 Y320.72266 Z4 E12552.714717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X190.558693 Y322.377511 Z4 E12560.735985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X189.409386 Y323.927172 Z4 E12568.757252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X188.113719 Y325.356719 Z4 E12576.77852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X186.684172 Y326.652386 Z4 E12584.799788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X185.134511 Y327.801693 Z4 E12592.821055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X183.47966 Y328.793572 Z4 E12600.842323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X181.735556 Y329.618472 Z4 E12608.86359 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X179.918997 Y330.268447 Z4 E12616.884858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X178.047476 Y330.737239 Z4 E12624.906125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X176.139017 Y331.020332 Z4 E12632.927393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X174.212 Y331.115 Z4 E12640.948661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X172.284983 Y331.020332 Z4 E12648.969928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X170.376524 Y330.737239 Z4 E12656.991196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X168.505003 Y330.268447 Z4 E12665.012463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X166.688444 Y329.618472 Z4 E12673.033731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X164.94434 Y328.793572 Z4 E12681.054999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X163.289489 Y327.801693 Z4 E12689.076266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X161.739828 Y326.652386 Z4 E12697.097534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X160.310281 Y325.356719 Z4 E12705.118801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X159.014614 Y323.927172 Z4 E12713.140069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X157.865307 Y322.377511 Z4 E12721.161336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X157.460183 Y321.701601 Z4 E12724.437555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X156.873428 Y320.72266 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=end-early tail
G1 X156.048528 Y318.978556 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=end-early tail
G1 X155.398553 Y317.161997 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0012
G0 X155.398553 Y317.161997 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0011 note=intra-page lift
G0 X136.285732 Y323.626086 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0011 note=intra-page XY
G0 X136.285732 Y323.626086 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0011 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0011
G1 X135.359472 Y322.446238 Z4 E12724.749369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X134.433212 Y321.266389 Z4 E12725.68481 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X133.506952 Y320.086541 Z4 E12727.243879 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X133.322625 Y319.85175 Z4 E12727.628535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X132.632131 Y318.868482 Z4 E12729.426575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X131.807523 Y317.694233 Z4 E12732.098087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X131.772155 Y317.639537 Z4 E12732.232899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X130.957675 Y316.379925 Z4 E12735.66285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X130.300689 Y315.363883 Z4 E12738.883959 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X130.153152 Y315.114156 Z4 E12739.716429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X129.390169 Y313.822701 Z4 E12744.393636 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X128.825101 Y312.866247 Z4 E12748.259541 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X128.641692 Y312.523089 Z4 E12749.69447 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X127.934634 Y311.200187 Z4 E12755.618931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=prime ramp
G1 X127.403734 Y310.206875 Z4 E12760.301491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X126.059565 Y307.391315 Z4 E12773.272789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X124.815568 Y304.425117 Z4 E12786.645433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X123.694721 Y301.313829 Z4 E12800.394444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X122.72 Y298.063 Z4 E12814.504282 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X125.970829 Y299.037721 Z4 E12828.614119 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X129.082117 Y300.158568 Z4 E12842.36313 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X132.048315 Y301.402565 Z4 E12855.735774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X134.863875 Y302.746734 Z4 E12868.707072 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X137.523247 Y304.168101 Z4 E12881.243584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X140.020883 Y305.643689 Z4 E12893.304357 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X142.351233 Y307.150523 Z4 E12904.841807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X144.50875 Y308.665625 Z4 E12915.802533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X148.283086 Y311.628732 Z4 E12935.752385 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X151.2995 Y314.349203 Z4 E12952.640152 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X153.513602 Y316.643229 Z4 E12965.895264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X154.881 Y318.327 Z4 E12974.91321 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X156.545807 Y319.876884 Z4 E12984.369822 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X157.982959 Y321.351584 Z4 E12992.930821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X159.203112 Y322.753614 Z4 E13000.658055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X160.216922 Y324.085484 Z4 E13007.617012 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X161.035047 Y325.349709 Z4 E13013.877618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X161.668143 Y326.548799 Z4 E13019.515045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X162.126866 Y327.685267 Z4 E13024.610314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X162.421875 Y328.761625 Z4 E13029.250328 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X162.563825 Y329.780385 Z4 E13033.52676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X162.563373 Y330.744061 Z4 E13037.533255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X162.431176 Y331.655162 Z4 E13041.360842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X162.177891 Y332.516203 Z4 E13045.092302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X161.814174 Y333.329695 Z4 E13048.797066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X161.350682 Y334.09815 Z4 E13052.528071 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X160.167 Y335.51 Z4 E13060.187862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X158.75515 Y336.693682 Z4 E13067.847653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X157.986695 Y337.157174 Z4 E13071.578659 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X157.173203 Y337.520891 Z4 E13075.283422 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X156.312162 Y337.774176 Z4 E13079.014883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X155.401061 Y337.906373 Z4 E13082.842469 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X154.437385 Y337.906825 Z4 E13086.848965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X153.418625 Y337.764875 Z4 E13091.125396 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X152.342267 Y337.469866 Z4 E13095.76541 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X151.205799 Y337.011143 Z4 E13100.86068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X150.006709 Y336.378047 Z4 E13106.498106 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X148.742484 Y335.559922 Z4 E13112.758713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X147.410614 Y334.546112 Z4 E13119.71767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X146.008584 Y333.325959 Z4 E13127.444904 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X144.533884 Y331.888807 Z4 E13136.005903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X142.984 Y330.224 Z4 E13145.462515 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X141.300229 Y328.856602 Z4 E13154.48046 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X139.681134 Y327.293916 Z4 E13163.835755 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X139.006203 Y326.6425 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=end-early tail
G1 X136.285732 Y323.626086 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0011
G0 X136.285732 Y323.626086 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0010 note=intra-page lift
G0 X120.914614 Y337.082828 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0010 note=intra-page XY
G0 X120.914614 Y337.082828 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0010 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0010
G1 X121.921953 Y335.971401 Z4 E13164.147569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X122.210281 Y335.653281 Z4 E13164.351614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X123.003587 Y334.93427 Z4 E13165.08301 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X123.639828 Y334.357614 Z4 E13165.89919 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X124.15494 Y333.975582 Z4 E13166.642079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X125.189489 Y333.208307 Z4 E13168.478483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X125.371308 Y333.099329 Z4 E13168.824776 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X126.657901 Y332.328175 Z4 E13171.631099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X126.84434 Y332.216428 Z4 E13172.089494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X128.00383 Y331.66803 Z4 E13175.061051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X128.588444 Y331.391528 Z4 E13176.732222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X129.391859 Y331.104062 Z4 E13179.11463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X130.405003 Y330.741553 Z4 E13182.406667 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X130.816252 Y330.638541 Z4 E13183.791836 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X132.271299 Y330.27407 Z4 E13189.09267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X132.276524 Y330.272761 Z4 E13189.11283 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X133.754961 Y330.053456 Z4 E13195.017132 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X134.184983 Y329.989668 Z4 E13196.824519 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X136.112 Y329.895 Z4 E13204.845787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X138.039017 Y329.989668 Z4 E13212.867055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X139.947476 Y330.272761 Z4 E13220.888322 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X141.818997 Y330.741553 Z4 E13228.90959 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X143.635556 Y331.391528 Z4 E13236.930857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X145.37966 Y332.216428 Z4 E13244.952125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X147.034511 Y333.208307 Z4 E13252.973393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X148.584172 Y334.357614 Z4 E13260.99466 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X150.013719 Y335.653281 Z4 E13269.015928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X151.309386 Y337.082828 Z4 E13277.037195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X152.458693 Y338.632489 Z4 E13285.058463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X153.450572 Y340.28734 Z4 E13293.07973 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X154.275472 Y342.031444 Z4 E13301.100998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X154.925447 Y343.848003 Z4 E13309.122266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X155.394239 Y345.719524 Z4 E13317.143533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X155.677332 Y347.627983 Z4 E13325.164801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X155.772 Y349.555 Z4 E13333.186068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X155.677332 Y351.482017 Z4 E13341.207336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X155.394239 Y353.390476 Z4 E13349.228604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X154.925447 Y355.261997 Z4 E13357.249871 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X154.275472 Y357.078556 Z4 E13365.271139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X153.450572 Y358.82266 Z4 E13373.292406 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X152.458693 Y360.477511 Z4 E13381.313674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X151.309386 Y362.027172 Z4 E13389.334942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X150.013719 Y363.456719 Z4 E13397.356209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X148.584172 Y364.752386 Z4 E13405.377477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X147.034511 Y365.901693 Z4 E13413.398744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X145.37966 Y366.893572 Z4 E13421.420012 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X143.635556 Y367.718472 Z4 E13429.441279 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X141.818997 Y368.368447 Z4 E13437.462547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X139.947476 Y368.837239 Z4 E13445.483815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X138.039017 Y369.120332 Z4 E13453.505082 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X136.112 Y369.215 Z4 E13461.52635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X134.184983 Y369.120332 Z4 E13469.547617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X132.276524 Y368.837239 Z4 E13477.568885 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X130.405003 Y368.368447 Z4 E13485.590153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X128.588444 Y367.718472 Z4 E13493.61142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X126.84434 Y366.893572 Z4 E13501.632688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X125.189489 Y365.901693 Z4 E13509.653955 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X123.639828 Y364.752386 Z4 E13517.675223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X122.210281 Y363.456719 Z4 E13525.696491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X120.914614 Y362.027172 Z4 E13533.717758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X119.765307 Y360.477511 Z4 E13541.739026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X118.773428 Y358.82266 Z4 E13549.760293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X117.948528 Y357.078556 Z4 E13557.781561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X117.298553 Y355.261997 Z4 E13565.802828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X116.829761 Y353.390476 Z4 E13573.824096 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X116.546668 Y351.482017 Z4 E13581.845364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X116.452 Y349.555 Z4 E13589.866631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X116.546668 Y347.627983 Z4 E13597.887899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X116.829761 Y345.719524 Z4 E13605.909166 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X117.298553 Y343.848003 Z4 E13613.930434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X117.948528 Y342.031444 Z4 E13621.951702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X118.285452 Y341.319079 Z4 E13625.22792 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X118.773428 Y340.28734 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=end-early tail
G1 X119.765307 Y338.632489 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=end-early tail
G1 X120.914614 Y337.082828 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0010
G0 X120.914614 Y337.082828 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0009 note=intra-page lift
G0 X110.991814 Y328.256907 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0009 note=intra-page XY
G0 X110.991814 Y328.256907 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0009 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0009
G1 X110.638531 Y327.226375 Z4 E13625.392392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.565877 Y326.82226 Z4 E13625.539734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.460469 Y326.235964 Z4 E13625.836572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.412999 Y325.332906 Z4 E13626.475175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.337642 Y323.899337 Z4 E13627.954432 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.340695 Y323.834958 Z4 E13628.034244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.402 Y322.542 Z4 E13629.880901 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.374023 Y322.338323 Z4 E13630.21694 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.225023 Y321.253572 Z4 E13632.203972 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.215525 Y320.84862 Z4 E13633.023264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.180375 Y319.350016 Z4 E13636.450762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.180442 Y319.349034 Z4 E13636.453215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.282826 Y317.852532 Z4 E13640.506794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.346102 Y316.92767 Z4 E13643.323774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.436429 Y316.361859 Z4 E13645.184001 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.672897 Y314.880615 Z4 E13650.484835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.80025 Y314.082875 Z4 E13653.598031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X110.973665 Y313.412793 Z4 E13656.409297 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X111.620867 Y310.911971 Z4 E13667.149043 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X112.192991 Y309.234334 Z4 E13674.518283 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X112.886 Y307.511297 Z4 E13682.23954 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X113.709649 Y305.754903 Z4 E13690.304822 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X114.673695 Y303.977193 Z4 E13698.712503 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X115.787894 Y302.190212 Z4 E13707.467746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X117.062 Y300.406 Z4 E13716.582819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X118.336106 Y302.190212 Z4 E13725.697893 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X119.450305 Y303.977193 Z4 E13734.453135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X120.414351 Y305.754903 Z4 E13742.860817 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X121.238 Y307.511297 Z4 E13750.926099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X121.931009 Y309.234334 Z4 E13758.647356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X122.503133 Y310.911971 Z4 E13766.016596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X123.32375 Y314.082875 Z4 E13779.634001 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X123.777898 Y316.92767 Z4 E13791.611048 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X123.943625 Y319.350016 Z4 E13801.705533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X123.898977 Y321.253572 Z4 E13809.621778 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X123.722 Y322.542 Z4 E13815.028735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X123.786358 Y323.899337 Z4 E13820.678226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X123.663531 Y326.235964 Z4 E13830.406205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X123.485469 Y327.226375 Z4 E13834.589874 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X122.918855 Y328.879195 Z4 E13841.854075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X122.539427 Y329.552726 Z4 E13845.06805 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X122.102 Y330.13175 Z4 E13848.085078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X121.611135 Y330.621829 Z4 E13850.968866 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X120.487339 Y331.357394 Z4 E13856.552911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X119.863531 Y331.614 Z4 E13859.357259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X118.514902 Y331.932664 Z4 E13865.118603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X117.062 Y332.029 Z4 E13871.172333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X115.609098 Y331.932664 Z4 E13877.226063 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X114.389078 Y331.644389 Z4 E13882.437987 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X114.260469 Y331.614 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X113.636661 Y331.357394 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X112.512865 Y330.621829 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X112.022 Y330.13175 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X111.584573 Y329.552726 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X111.205145 Y328.879195 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
G1 X110.991814 Y328.256907 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0009
G0 X110.991814 Y328.256907 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0008 note=intra-page lift
G0 X77.020166 Y339.902932 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0008 note=intra-page XY
G0 X77.020166 Y339.902932 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0008 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0008
G1 X77.250572 Y340.28734 Z4 E13882.465822 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X77.700287 Y341.238183 Z4 E13882.749801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X78.075472 Y342.031444 Z4 E13883.221341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X78.285182 Y342.617544 Z4 E13883.685242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X78.725447 Y343.848003 Z4 E13885.008576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X78.772378 Y344.035363 Z4 E13885.244311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.136848 Y345.490409 Z4 E13887.427007 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.194239 Y345.719524 Z4 E13887.827529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.379678 Y346.969652 Z4 E13890.233331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.477332 Y347.627983 Z4 E13891.6782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.518277 Y348.461444 Z4 E13893.663282 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.572 Y349.555 Z4 E13896.560587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.552121 Y349.959637 Z4 E13897.716861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.47852 Y351.45783 Z4 E13902.394068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.477332 Y351.482017 Z4 E13902.474692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.260789 Y352.941828 Z4 E13907.694902 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X79.194239 Y353.390476 Z4 E13909.420515 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X78.939974 Y354.405558 Z4 E13913.619363 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X78.725447 Y355.261997 Z4 E13917.290027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X78.075472 Y357.078556 Z4 E13925.311294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X77.250572 Y358.82266 Z4 E13933.332562 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X76.258693 Y360.477511 Z4 E13941.35383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X75.109386 Y362.027172 Z4 E13949.375097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X73.813719 Y363.456719 Z4 E13957.396365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X72.384172 Y364.752386 Z4 E13965.417632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X70.834511 Y365.901693 Z4 E13973.4389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X69.17966 Y366.893572 Z4 E13981.460168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X67.435556 Y367.718472 Z4 E13989.481435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X65.618997 Y368.368447 Z4 E13997.502703 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X63.747476 Y368.837239 Z4 E14005.52397 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X61.839017 Y369.120332 Z4 E14013.545238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X59.912 Y369.215 Z4 E14021.566505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X57.984983 Y369.120332 Z4 E14029.587773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X56.076524 Y368.837239 Z4 E14037.609041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X54.205003 Y368.368447 Z4 E14045.630308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X52.388444 Y367.718472 Z4 E14053.651576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X50.64434 Y366.893572 Z4 E14061.672843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X48.989489 Y365.901693 Z4 E14069.694111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X47.439828 Y364.752386 Z4 E14077.715379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X46.010281 Y363.456719 Z4 E14085.736646 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X44.714614 Y362.027172 Z4 E14093.757914 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X43.565307 Y360.477511 Z4 E14101.779181 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X42.573428 Y358.82266 Z4 E14109.800449 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X41.748528 Y357.078556 Z4 E14117.821716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X41.098553 Y355.261997 Z4 E14125.842984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X40.629761 Y353.390476 Z4 E14133.864252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X40.346668 Y351.482017 Z4 E14141.885519 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X40.252 Y349.555 Z4 E14149.906787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X40.346668 Y347.627983 Z4 E14157.928054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X40.629761 Y345.719524 Z4 E14165.949322 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X41.098553 Y343.848003 Z4 E14173.97059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X41.748528 Y342.031444 Z4 E14181.991857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X42.573428 Y340.28734 Z4 E14190.013125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X43.565307 Y338.632489 Z4 E14198.034392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X44.714614 Y337.082828 Z4 E14206.05566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X46.010281 Y335.653281 Z4 E14214.076928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X47.439828 Y334.357614 Z4 E14222.098195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X48.989489 Y333.208307 Z4 E14230.119463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X50.64434 Y332.216428 Z4 E14238.14073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X52.388444 Y331.391528 Z4 E14246.161998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X54.205003 Y330.741553 Z4 E14254.183265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X56.076524 Y330.272761 Z4 E14262.204533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X57.984983 Y329.989668 Z4 E14270.225801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X59.912 Y329.895 Z4 E14278.247068 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X61.839017 Y329.989668 Z4 E14286.268336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X63.747476 Y330.272761 Z4 E14294.289603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X65.618997 Y330.741553 Z4 E14302.310871 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X67.435556 Y331.391528 Z4 E14310.332139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X69.17966 Y332.216428 Z4 E14318.353406 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X70.834511 Y333.208307 Z4 E14326.374674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X72.384172 Y334.357614 Z4 E14334.395941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X73.813719 Y335.653281 Z4 E14342.417209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X74.04195 Y335.905095 Z4 E14343.830151 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X75.109386 Y337.082828 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
G1 X76.258693 Y338.632489 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
G1 X77.020166 Y339.902932 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0008
G0 X77.020166 Y339.902932 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0007 note=intra-page lift
G0 X92.305003 Y330.741553 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0007 note=intra-page XY
G0 X92.305003 Y330.741553 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0007 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0007
G1 X93.76005 Y330.377083 Z4 E14344.141965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X94.176524 Y330.272761 Z4 E14344.34601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X95.235595 Y330.115663 Z4 E14345.077407 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X96.084983 Y329.989668 Z4 E14345.893586 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X96.725529 Y329.9582 Z4 E14346.636475 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X98.012 Y329.895 Z4 E14348.472879 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X98.223722 Y329.905401 Z4 E14348.819172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X99.721915 Y329.979003 Z4 E14351.625496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X99.939017 Y329.989668 Z4 E14352.08389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X101.207771 Y330.17787 Z4 E14355.055447 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X101.847476 Y330.272761 Z4 E14356.726618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X102.675199 Y330.480095 Z4 E14359.109026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X103.718997 Y330.741553 Z4 E14362.401064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X104.118168 Y330.884379 Z4 E14363.786232 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X105.530484 Y331.389714 Z4 E14369.087066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X105.535556 Y331.391528 Z4 E14369.107226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X106.886671 Y332.030558 Z4 E14375.011528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=prime ramp
G1 X107.27966 Y332.216428 Z4 E14376.818916 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X108.934511 Y333.208307 Z4 E14384.840183 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X110.484172 Y334.357614 Z4 E14392.861451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X111.913719 Y335.653281 Z4 E14400.882718 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X113.209386 Y337.082828 Z4 E14408.903986 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X114.358693 Y338.632489 Z4 E14416.925253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X115.350572 Y340.28734 Z4 E14424.946521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X116.175472 Y342.031444 Z4 E14432.967789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X116.825447 Y343.848003 Z4 E14440.989056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X117.294239 Y345.719524 Z4 E14449.010324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X117.577332 Y347.627983 Z4 E14457.031591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X117.672 Y349.555 Z4 E14465.052859 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X117.577332 Y351.482017 Z4 E14473.074127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X117.294239 Y353.390476 Z4 E14481.095394 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X116.825447 Y355.261997 Z4 E14489.116662 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X116.175472 Y357.078556 Z4 E14497.137929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X115.350572 Y358.82266 Z4 E14505.159197 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X114.358693 Y360.477511 Z4 E14513.180465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X113.209386 Y362.027172 Z4 E14521.201732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X111.913719 Y363.456719 Z4 E14529.223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X110.484172 Y364.752386 Z4 E14537.244267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X108.934511 Y365.901693 Z4 E14545.265535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X107.27966 Y366.893572 Z4 E14553.286802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X105.535556 Y367.718472 Z4 E14561.30807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X103.718997 Y368.368447 Z4 E14569.329338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X101.847476 Y368.837239 Z4 E14577.350605 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X99.939017 Y369.120332 Z4 E14585.371873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X98.012 Y369.215 Z4 E14593.39314 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X96.084983 Y369.120332 Z4 E14601.414408 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X94.176524 Y368.837239 Z4 E14609.435676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X92.305003 Y368.368447 Z4 E14617.456943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X90.488444 Y367.718472 Z4 E14625.478211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X88.74434 Y366.893572 Z4 E14633.499478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X87.089489 Y365.901693 Z4 E14641.520746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X85.539828 Y364.752386 Z4 E14649.542014 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X84.110281 Y363.456719 Z4 E14657.563281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X82.814614 Y362.027172 Z4 E14665.584549 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X81.665307 Y360.477511 Z4 E14673.605816 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X80.673428 Y358.82266 Z4 E14681.627084 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X79.848528 Y357.078556 Z4 E14689.648351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X79.198553 Y355.261997 Z4 E14697.669619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X78.729761 Y353.390476 Z4 E14705.690887 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X78.446668 Y351.482017 Z4 E14713.712154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X78.352 Y349.555 Z4 E14721.733422 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X78.446668 Y347.627983 Z4 E14729.754689 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X78.729761 Y345.719524 Z4 E14737.775957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X79.198553 Y343.848003 Z4 E14745.797225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X79.848528 Y342.031444 Z4 E14753.818492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X80.673428 Y340.28734 Z4 E14761.83976 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X81.665307 Y338.632489 Z4 E14769.861027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X82.814614 Y337.082828 Z4 E14777.882295 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X84.110281 Y335.653281 Z4 E14785.903562 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X85.539828 Y334.357614 Z4 E14793.92483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X87.089489 Y333.208307 Z4 E14801.946098 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X87.765399 Y332.803183 Z4 E14805.222316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X88.74434 Y332.216428 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=end-early tail
G1 X90.488444 Y331.391528 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=end-early tail
G1 X92.305003 Y330.741553 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0007
G0 X92.305003 Y330.741553 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0006 note=intra-page lift
G0 X85.840914 Y311.628732 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0006 note=intra-page XY
G0 X85.840914 Y311.628732 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0006 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0006
G1 X87.020762 Y310.702472 Z4 E14805.53413 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X88.200611 Y309.776212 Z4 E14806.469571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X89.380459 Y308.849952 Z4 E14808.02864 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X89.61525 Y308.665625 Z4 E14808.413296 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X90.598518 Y307.975131 Z4 E14810.211336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X91.772767 Y307.150523 Z4 E14812.882848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X91.827463 Y307.115155 Z4 E14813.01766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X93.087075 Y306.300675 Z4 E14816.447612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X94.103117 Y305.643689 Z4 E14819.66872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X94.352844 Y305.496152 Z4 E14820.501191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X95.644299 Y304.733169 Z4 E14825.178397 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X96.600753 Y304.168101 Z4 E14829.044303 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X96.943911 Y303.984692 Z4 E14830.479231 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X98.266813 Y303.277634 Z4 E14836.403693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X99.260125 Y302.746734 Z4 E14841.086252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X102.075685 Y301.402565 Z4 E14854.05755 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X105.041883 Y300.158568 Z4 E14867.430194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X108.153171 Y299.037721 Z4 E14881.179205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X111.404 Y298.063 Z4 E14895.289043 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X110.429279 Y301.313829 Z4 E14909.398881 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X109.308432 Y304.425117 Z4 E14923.147891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X108.064435 Y307.391315 Z4 E14936.520535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X106.720266 Y310.206875 Z4 E14949.491833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X105.298899 Y312.866247 Z4 E14962.028345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X103.823311 Y315.363883 Z4 E14974.089118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X102.316477 Y317.694233 Z4 E14985.626569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X100.801375 Y319.85175 Z4 E14996.587295 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X97.838268 Y323.626086 Z4 E15016.537146 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X95.117797 Y326.6425 Z4 E15033.424913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X92.823771 Y328.856602 Z4 E15046.680025 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X91.14 Y330.224 Z4 E15055.697971 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X89.590116 Y331.888807 Z4 E15065.154583 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X88.115416 Y333.325959 Z4 E15073.715582 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X86.713386 Y334.546112 Z4 E15081.442816 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X85.381516 Y335.559922 Z4 E15088.401773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X84.117291 Y336.378047 Z4 E15094.662379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X82.918201 Y337.011143 Z4 E15100.299806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X81.781733 Y337.469866 Z4 E15105.395075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X80.705375 Y337.764875 Z4 E15110.035089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X79.686615 Y337.906825 Z4 E15114.311521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X78.722939 Y337.906373 Z4 E15118.318017 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X77.811838 Y337.774176 Z4 E15122.145603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X76.950797 Y337.520891 Z4 E15125.877064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X76.137305 Y337.157174 Z4 E15129.581827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X75.36885 Y336.693682 Z4 E15133.312833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X73.957 Y335.51 Z4 E15140.972623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X72.773318 Y334.09815 Z4 E15148.632414 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X72.309826 Y333.329695 Z4 E15152.36342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X71.946109 Y332.516203 Z4 E15156.068183 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X71.692824 Y331.655162 Z4 E15159.799644 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X71.560627 Y330.744061 Z4 E15163.62723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X71.560175 Y329.780385 Z4 E15167.633726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X71.702125 Y328.761625 Z4 E15171.910158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X71.997134 Y327.685267 Z4 E15176.550172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X72.455857 Y326.548799 Z4 E15181.645441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X73.088953 Y325.349709 Z4 E15187.282867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X73.907078 Y324.085484 Z4 E15193.543474 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X74.920888 Y322.753614 Z4 E15200.502431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X76.141041 Y321.351584 Z4 E15208.229665 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X77.578193 Y319.876884 Z4 E15216.790664 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X79.243 Y318.327 Z4 E15226.247276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X80.610398 Y316.643229 Z4 E15235.265222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X82.173084 Y315.024134 Z4 E15244.620517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X82.8245 Y314.349203 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
G1 X85.840914 Y311.628732 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0006
G0 X85.840914 Y311.628732 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0005 note=intra-page lift
G0 X72.384172 Y296.257614 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0005 note=intra-page XY
G0 X72.384172 Y296.257614 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0005 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0005
G1 X73.495599 Y297.264953 Z4 E15244.93233 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X73.813719 Y297.553281 Z4 E15245.136375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X74.53273 Y298.346587 Z4 E15245.867772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X75.109386 Y298.982828 Z4 E15246.683951 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X75.491418 Y299.49794 Z4 E15247.42684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X76.258693 Y300.532489 Z4 E15249.263245 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X76.367671 Y300.714308 Z4 E15249.609537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X77.138825 Y302.000901 Z4 E15252.415861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X77.250572 Y302.18734 Z4 E15252.874255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X77.79897 Y303.34683 Z4 E15255.845812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X78.075472 Y303.931444 Z4 E15257.516983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X78.362938 Y304.734859 Z4 E15259.899391 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X78.725447 Y305.748003 Z4 E15263.191429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X78.828459 Y306.159252 Z4 E15264.576598 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X79.19293 Y307.614299 Z4 E15269.877432 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X79.194239 Y307.619524 Z4 E15269.897591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X79.413544 Y309.097961 Z4 E15275.801893 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X79.477332 Y309.527983 Z4 E15277.609281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X79.572 Y311.455 Z4 E15285.630548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X79.477332 Y313.382017 Z4 E15293.651816 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X79.194239 Y315.290476 Z4 E15301.673083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X78.725447 Y317.161997 Z4 E15309.694351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X78.075472 Y318.978556 Z4 E15317.715619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X77.250572 Y320.72266 Z4 E15325.736886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X76.258693 Y322.377511 Z4 E15333.758154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X75.109386 Y323.927172 Z4 E15341.779421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X73.813719 Y325.356719 Z4 E15349.800689 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X72.384172 Y326.652386 Z4 E15357.821956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X70.834511 Y327.801693 Z4 E15365.843224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X69.17966 Y328.793572 Z4 E15373.864492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X67.435556 Y329.618472 Z4 E15381.885759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X65.618997 Y330.268447 Z4 E15389.907027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X63.747476 Y330.737239 Z4 E15397.928294 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X61.839017 Y331.020332 Z4 E15405.949562 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X59.912 Y331.115 Z4 E15413.97083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X57.984983 Y331.020332 Z4 E15421.992097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X56.076524 Y330.737239 Z4 E15430.013365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X54.205003 Y330.268447 Z4 E15438.034632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X52.388444 Y329.618472 Z4 E15446.0559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X50.64434 Y328.793572 Z4 E15454.077168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X48.989489 Y327.801693 Z4 E15462.098435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X47.439828 Y326.652386 Z4 E15470.119703 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X46.010281 Y325.356719 Z4 E15478.14097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X44.714614 Y323.927172 Z4 E15486.162238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X43.565307 Y322.377511 Z4 E15494.183505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X42.573428 Y320.72266 Z4 E15502.204773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X41.748528 Y318.978556 Z4 E15510.226041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X41.098553 Y317.161997 Z4 E15518.247308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X40.629761 Y315.290476 Z4 E15526.268576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X40.346668 Y313.382017 Z4 E15534.289843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X40.252 Y311.455 Z4 E15542.311111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X40.346668 Y309.527983 Z4 E15550.332379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X40.629761 Y307.619524 Z4 E15558.353646 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X41.098553 Y305.748003 Z4 E15566.374914 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X41.748528 Y303.931444 Z4 E15574.396181 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X42.573428 Y302.18734 Z4 E15582.417449 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X43.565307 Y300.532489 Z4 E15590.438717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X44.714614 Y298.982828 Z4 E15598.459984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X46.010281 Y297.553281 Z4 E15606.481252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X47.439828 Y296.257614 Z4 E15614.502519 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X48.989489 Y295.108307 Z4 E15622.523787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X50.64434 Y294.116428 Z4 E15630.545054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X52.388444 Y293.291528 Z4 E15638.566322 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X54.205003 Y292.641553 Z4 E15646.58759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X56.076524 Y292.172761 Z4 E15654.608857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X57.984983 Y291.889668 Z4 E15662.630125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X59.912 Y291.795 Z4 E15670.651392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X61.839017 Y291.889668 Z4 E15678.67266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X63.747476 Y292.172761 Z4 E15686.693928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X65.618997 Y292.641553 Z4 E15694.715195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X67.435556 Y293.291528 Z4 E15702.736463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X68.147921 Y293.628452 Z4 E15706.012681 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X69.17966 Y294.116428 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=end-early tail
G1 X70.834511 Y295.108307 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=end-early tail
G1 X72.384172 Y296.257614 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0005
G0 X72.384172 Y296.257614 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0004 note=intra-page lift
G0 X81.287865 Y286.308153 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0004 note=intra-page XY
G0 X81.287865 Y286.308153 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0004 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0004
G1 X82.240625 Y285.981531 Z4 E15706.153265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X82.725658 Y285.894329 Z4 E15706.324495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X83.231036 Y285.803469 Z4 E15706.574515 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X84.216195 Y285.751683 Z4 E15707.259936 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X85.567663 Y285.680642 Z4 E15708.639056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X85.714164 Y285.687588 Z4 E15708.819005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X86.925 Y285.745 Z4 E15710.53456 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X87.210127 Y285.705835 Z4 E15711.001701 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X88.213428 Y285.568023 Z4 E15712.827996 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X88.700572 Y285.556597 Z4 E15713.808025 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X90.116984 Y285.523375 Z4 E15717.031397 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X90.199989 Y285.529054 Z4 E15717.237977 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X91.696491 Y285.631438 Z4 E15721.291556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X92.53933 Y285.689102 Z4 E15723.849081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X93.186328 Y285.792389 Z4 E15725.968762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X94.667571 Y286.028858 Z4 E15731.269596 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X95.384125 Y286.14325 Z4 E15734.057692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X96.1338 Y286.337263 Z4 E15737.194058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=prime ramp
G1 X98.555029 Y286.963867 Z4 E15747.591995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X100.232666 Y287.535991 Z4 E15754.961235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X101.955703 Y288.229 Z4 E15762.682492 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X103.712097 Y289.052649 Z4 E15770.747774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X105.489807 Y290.016695 Z4 E15779.155455 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X107.276788 Y291.130894 Z4 E15787.910698 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X109.061 Y292.405 Z4 E15797.025771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X107.276788 Y293.679106 Z4 E15806.140845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X105.489807 Y294.793305 Z4 E15814.896087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X103.712097 Y295.757351 Z4 E15823.303769 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X101.955703 Y296.581 Z4 E15831.369051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X100.232666 Y297.274009 Z4 E15839.090308 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X98.555029 Y297.846133 Z4 E15846.459548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X95.384125 Y298.66675 Z4 E15860.076953 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X92.53933 Y299.120898 Z4 E15872.054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X90.116984 Y299.286625 Z4 E15882.148485 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X88.213428 Y299.241977 Z4 E15890.06473 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X86.925 Y299.065 Z4 E15895.471687 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X85.567663 Y299.129358 Z4 E15901.121178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X83.231036 Y299.006531 Z4 E15910.849157 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X82.240625 Y298.828469 Z4 E15915.032826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X80.587805 Y298.261855 Z4 E15922.297027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X79.914274 Y297.882427 Z4 E15925.511002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X79.33525 Y297.445 Z4 E15928.52803 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X78.845171 Y296.954135 Z4 E15931.411818 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X78.109606 Y295.830339 Z4 E15936.995863 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X77.853 Y295.206531 Z4 E15939.800211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X77.534336 Y293.857902 Z4 E15945.561555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X77.438 Y292.405 Z4 E15951.615285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X77.534336 Y290.952098 Z4 E15957.669015 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X77.841517 Y289.652067 Z4 E15963.222748 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004
G1 X77.853 Y289.603469 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X78.109606 Y288.979661 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X78.845171 Y287.855865 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X79.33525 Y287.365 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X79.914274 Y286.927573 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X80.587805 Y286.548145 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
G1 X81.287865 Y286.308153 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0004
G0 X81.287865 Y286.308153 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0003 note=intra-page lift
G0 X71.382815 Y257.414957 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0003 note=intra-page XY
G0 X71.382815 Y257.414957 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0003 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0003
G1 X72.384172 Y258.157614 Z4 E15963.438143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X72.571857 Y258.327722 Z4 E15963.534562 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X73.683283 Y259.33506 Z4 E15964.470003 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X73.813719 Y259.453281 Z4 E15964.620675 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X74.702837 Y260.434271 Z4 E15966.029072 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X75.109386 Y260.882828 Z4 E15966.834924 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X75.64231 Y261.601394 Z4 E15968.211768 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X76.258693 Y262.432489 Z4 E15970.08089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X76.497894 Y262.831573 Z4 E15971.018092 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X77.250572 Y264.08734 Z4 E15974.358574 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X77.265938 Y264.119828 Z4 E15974.448044 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X77.90727 Y265.475812 Z4 E15978.501623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X78.075472 Y265.831444 Z4 E15979.667975 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X78.448273 Y266.873354 Z4 E15983.178829 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X78.725447 Y267.648003 Z4 E15986.009094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X78.890007 Y268.304963 Z4 E15988.479663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X79.194239 Y269.519524 Z4 E15993.381929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X79.230615 Y269.764756 Z4 E15994.404125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=prime ramp
G1 X79.477332 Y271.427983 Z4 E16001.394679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X79.572 Y273.355 Z4 E16009.415947 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X79.477332 Y275.282017 Z4 E16017.437214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X79.194239 Y277.190476 Z4 E16025.458482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X78.725447 Y279.061997 Z4 E16033.47975 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X78.075472 Y280.878556 Z4 E16041.501017 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X77.250572 Y282.62266 Z4 E16049.522285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X76.258693 Y284.277511 Z4 E16057.543552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X75.109386 Y285.827172 Z4 E16065.56482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X73.813719 Y287.256719 Z4 E16073.586088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X72.384172 Y288.552386 Z4 E16081.607355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X70.834511 Y289.701693 Z4 E16089.628623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X69.17966 Y290.693572 Z4 E16097.64989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X67.435556 Y291.518472 Z4 E16105.671158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X65.618997 Y292.168447 Z4 E16113.692425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X63.747476 Y292.637239 Z4 E16121.713693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X61.839017 Y292.920332 Z4 E16129.734961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X59.912 Y293.015 Z4 E16137.756228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X57.984983 Y292.920332 Z4 E16145.777496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X56.076524 Y292.637239 Z4 E16153.798763 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X54.205003 Y292.168447 Z4 E16161.820031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X52.388444 Y291.518472 Z4 E16169.841299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X50.64434 Y290.693572 Z4 E16177.862566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X48.989489 Y289.701693 Z4 E16185.883834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X47.439828 Y288.552386 Z4 E16193.905101 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X46.010281 Y287.256719 Z4 E16201.926369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X44.714614 Y285.827172 Z4 E16209.947637 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X43.565307 Y284.277511 Z4 E16217.968904 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X42.573428 Y282.62266 Z4 E16225.990172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X41.748528 Y280.878556 Z4 E16234.011439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X41.098553 Y279.061997 Z4 E16242.032707 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X40.629761 Y277.190476 Z4 E16250.053974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X40.346668 Y275.282017 Z4 E16258.075242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X40.252 Y273.355 Z4 E16266.09651 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X40.346668 Y271.427983 Z4 E16274.117777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X40.629761 Y269.519524 Z4 E16282.139045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X41.098553 Y267.648003 Z4 E16290.160312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X41.748528 Y265.831444 Z4 E16298.18158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X42.573428 Y264.08734 Z4 E16306.202848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X43.565307 Y262.432489 Z4 E16314.224115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X44.714614 Y260.882828 Z4 E16322.245383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X46.010281 Y259.453281 Z4 E16330.26665 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X47.439828 Y258.157614 Z4 E16338.287918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X48.989489 Y257.008307 Z4 E16346.309186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X50.64434 Y256.016428 Z4 E16354.330453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X52.388444 Y255.191528 Z4 E16362.351721 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X54.205003 Y254.541553 Z4 E16370.372988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X56.076524 Y254.072761 Z4 E16378.394256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X57.984983 Y253.789668 Z4 E16386.415523 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X59.912 Y253.695 Z4 E16394.436791 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X61.839017 Y253.789668 Z4 E16402.458059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X63.747476 Y254.072761 Z4 E16410.479326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X65.618997 Y254.541553 Z4 E16418.500594 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X67.003694 Y255.037005 Z4 E16424.614913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003
G1 X67.435556 Y255.191528 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
G1 X69.17966 Y256.016428 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
G1 X70.834511 Y257.008307 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
G1 X71.382815 Y257.414957 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0003
G0 X71.382815 Y257.414957 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0002 note=intra-page lift
G0 X79.178707 Y246.903413 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0002 note=intra-page XY
G0 X79.178707 Y246.903413 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0002
G1 X79.686615 Y246.903175 Z4 E16424.650663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X80.669215 Y247.040087 Z4 E16424.926726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X80.705375 Y247.045125 Z4 E16424.94209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X81.781733 Y247.340134 Z4 E16425.590002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X82.103914 Y247.470179 Z4 E16425.862168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X82.918201 Y247.798857 Z4 E16426.699188 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X83.468137 Y248.089213 Z4 E16427.421237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X84.117291 Y248.431953 Z4 E16428.4115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X84.760313 Y248.848076 Z4 E16429.603933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X85.381516 Y249.250078 Z4 E16430.910319 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X85.986306 Y249.71044 Z4 E16432.410257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X86.713386 Y250.263888 Z4 E16434.425448 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X87.155613 Y250.648747 Z4 E16435.840208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X88.115416 Y251.484041 Z4 E16439.238518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X88.278433 Y251.642908 Z4 E16439.893787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X89.352682 Y252.689803 Z4 E16444.570994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X89.590116 Y252.921193 Z4 E16445.68892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X90.386299 Y253.776412 Z4 E16449.871828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X91.14 Y254.586 Z4 E16454.180219 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X91.445756 Y254.834306 Z4 E16455.796289 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X92.823771 Y255.953398 Z4 E16463.176664 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X95.117797 Y258.1675 Z4 E16476.431776 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X97.838268 Y261.183914 Z4 E16493.319543 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X100.801375 Y264.95825 Z4 E16513.269395 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X102.316477 Y267.115767 Z4 E16524.230121 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X103.823311 Y269.446117 Z4 E16535.767571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X105.298899 Y271.943753 Z4 E16547.828344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X106.720266 Y274.603125 Z4 E16560.364856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X108.064435 Y277.418685 Z4 E16573.336154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X109.308432 Y280.384883 Z4 E16586.708798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X110.429279 Y283.496171 Z4 E16600.457809 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X111.404 Y286.747 Z4 E16614.567647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X108.153171 Y285.772279 Z4 E16628.677484 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X105.041883 Y284.651432 Z4 E16642.426495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X102.075685 Y283.407435 Z4 E16655.799139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X99.260125 Y282.063266 Z4 E16668.770437 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X96.600753 Y280.641899 Z4 E16681.306949 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X94.103117 Y279.166311 Z4 E16693.367722 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X91.772767 Y277.659477 Z4 E16704.905172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X89.61525 Y276.144375 Z4 E16715.865898 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X85.840914 Y273.181268 Z4 E16735.81575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X82.8245 Y270.460797 Z4 E16752.703517 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X80.610398 Y268.166771 Z4 E16765.958629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X79.243 Y266.483 Z4 E16774.976575 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X77.578193 Y264.933116 Z4 E16784.433187 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X76.141041 Y263.458416 Z4 E16792.994186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X74.920888 Y262.056386 Z4 E16800.72142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X73.907078 Y260.724516 Z4 E16807.680377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X73.088953 Y259.460291 Z4 E16813.940983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X72.455857 Y258.261201 Z4 E16819.57841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X71.997134 Y257.124733 Z4 E16824.673679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X71.702125 Y256.048375 Z4 E16829.313693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X71.560175 Y255.029615 Z4 E16833.590125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X71.560627 Y254.065939 Z4 E16837.59662 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X71.692824 Y253.154838 Z4 E16841.424207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X71.946109 Y252.293797 Z4 E16845.155667 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X72.309826 Y251.480305 Z4 E16848.860431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X72.773318 Y250.71185 Z4 E16852.591436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X73.957 Y249.3 Z4 E16860.251227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X74.650389 Y248.718669 Z4 E16864.013113 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X75.36885 Y248.116318 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X76.137305 Y247.652826 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X76.950797 Y247.289109 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X77.811838 Y247.035824 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X78.722939 Y246.903627 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X79.178707 Y246.903413 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0002
G0 X79.178707 Y246.903413 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0001 note=intra-page lift
G0 X79.170621 Y229.659514 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0001 note=intra-page XY
G0 X79.170621 Y229.659514 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0001
G1 X79.198553 Y229.548003 Z4 E16864.014944 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X79.66516 Y228.243923 Z4 E16864.324927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X79.848528 Y227.731444 Z4 E16864.592276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X80.257144 Y226.867498 Z4 E16865.260368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X80.673428 Y225.98734 Z4 E16866.201324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X80.944032 Y225.535864 Z4 E16866.819437 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X81.665307 Y224.332489 Z4 E16868.84209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X81.723103 Y224.254561 Z4 E16869.002133 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X82.616652 Y223.049749 Z4 E16871.808457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X82.814614 Y222.782828 Z4 E16872.514573 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X83.598781 Y221.917634 Z4 E16875.238409 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X84.110281 Y221.353281 Z4 E16877.218774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X84.657354 Y220.857442 Z4 E16879.291988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X85.539828 Y220.057614 Z4 E16882.954692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X85.788018 Y219.873544 Z4 E16883.969194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X86.99283 Y218.979995 Z4 E16889.270028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X87.089489 Y218.908307 Z4 E16889.722327 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X88.272861 Y218.199021 Z4 E16895.19449 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X88.74434 Y217.916428 Z4 E16897.479806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X90.488444 Y217.091528 Z4 E16905.501074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X92.305003 Y216.441553 Z4 E16913.522341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X94.176524 Y215.972761 Z4 E16921.543609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X96.084983 Y215.689668 Z4 E16929.564876 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X98.012 Y215.595 Z4 E16937.586144 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X99.939017 Y215.689668 Z4 E16945.607412 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X101.847476 Y215.972761 Z4 E16953.628679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X103.718997 Y216.441553 Z4 E16961.649947 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X105.535556 Y217.091528 Z4 E16969.671214 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X107.27966 Y217.916428 Z4 E16977.692482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X108.934511 Y218.908307 Z4 E16985.71375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X110.484172 Y220.057614 Z4 E16993.735017 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X111.913719 Y221.353281 Z4 E17001.756285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X113.209386 Y222.782828 Z4 E17009.777552 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X114.358693 Y224.332489 Z4 E17017.79882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X115.350572 Y225.98734 Z4 E17025.820088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X116.175472 Y227.731444 Z4 E17033.841355 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X116.825447 Y229.548003 Z4 E17041.862623 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X117.294239 Y231.419524 Z4 E17049.88389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X117.577332 Y233.327983 Z4 E17057.905158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X117.672 Y235.255 Z4 E17065.926425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X117.577332 Y237.182017 Z4 E17073.947693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X117.294239 Y239.090476 Z4 E17081.968961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X116.825447 Y240.961997 Z4 E17089.990228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X116.175472 Y242.778556 Z4 E17098.011496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X115.350572 Y244.52266 Z4 E17106.032763 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X114.358693 Y246.177511 Z4 E17114.054031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X113.209386 Y247.727172 Z4 E17122.075299 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X111.913719 Y249.156719 Z4 E17130.096566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X110.484172 Y250.452386 Z4 E17138.117834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X108.934511 Y251.601693 Z4 E17146.139101 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X107.27966 Y252.593572 Z4 E17154.160369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X105.535556 Y253.418472 Z4 E17162.181637 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X103.718997 Y254.068447 Z4 E17170.202904 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X101.847476 Y254.537239 Z4 E17178.224172 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X99.939017 Y254.820332 Z4 E17186.245439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X98.012 Y254.915 Z4 E17194.266707 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X96.084983 Y254.820332 Z4 E17202.287974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X94.176524 Y254.537239 Z4 E17210.309242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X92.305003 Y254.068447 Z4 E17218.33051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X90.488444 Y253.418472 Z4 E17226.351777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X88.74434 Y252.593572 Z4 E17234.373045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X87.089489 Y251.601693 Z4 E17242.394312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X85.539828 Y250.452386 Z4 E17250.41558 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X84.110281 Y249.156719 Z4 E17258.436848 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X82.814614 Y247.727172 Z4 E17266.458115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X81.665307 Y246.177511 Z4 E17274.479383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X80.673428 Y244.52266 Z4 E17282.50065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X79.848528 Y242.778556 Z4 E17290.521918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X79.198553 Y240.961997 Z4 E17298.543186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X78.729761 Y239.090476 Z4 E17306.564453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X78.446668 Y237.182017 Z4 E17314.585721 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X78.352 Y235.255 Z4 E17322.606988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X78.385026 Y234.582743 Z4 E17325.405278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X78.446668 Y233.327983 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=end-early tail
G1 X78.729761 Y231.419524 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=end-early tail
G1 X79.170621 Y229.659514 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0001
G0 X79.170621 Y229.659514 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0000 note=intra-page lift
G0 X46.010281 Y221.353281 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0000 note=intra-page XY
G0 X46.010281 Y221.353281 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0000 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0000
G1 X47.121707 Y220.345942 Z4 E17325.717091 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X47.439828 Y220.057614 Z4 E17325.921136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X48.299789 Y219.419824 Z4 E17326.652533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X48.989489 Y218.908307 Z4 E17327.468712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X49.539566 Y218.578604 Z4 E17328.211602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X50.64434 Y217.916428 Z4 E17330.048006 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X50.835965 Y217.825796 Z4 E17330.394298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X52.191949 Y217.184463 Z4 E17333.200622 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X52.388444 Y217.091528 Z4 E17333.659016 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X53.596102 Y216.659421 Z4 E17336.630573 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X54.205003 Y216.441553 Z4 E17338.301744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X55.032726 Y216.234219 Z4 E17340.684152 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X56.076524 Y215.972761 Z4 E17343.97619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X56.49589 Y215.910554 Z4 E17345.361359 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X57.979655 Y215.690459 Z4 E17350.662193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X57.984983 Y215.689668 Z4 E17350.682352 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X59.477796 Y215.616331 Z4 E17356.586654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X59.912 Y215.595 Z4 E17358.394042 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X61.839017 Y215.689668 Z4 E17366.415309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X63.747476 Y215.972761 Z4 E17374.436577 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X65.618997 Y216.441553 Z4 E17382.457845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X67.435556 Y217.091528 Z4 E17390.479112 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X69.17966 Y217.916428 Z4 E17398.50038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X70.834511 Y218.908307 Z4 E17406.521647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X72.384172 Y220.057614 Z4 E17414.542915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X73.813719 Y221.353281 Z4 E17422.564182 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X75.109386 Y222.782828 Z4 E17430.58545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X76.258693 Y224.332489 Z4 E17438.606718 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X77.250572 Y225.98734 Z4 E17446.627985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X78.075472 Y227.731444 Z4 E17454.649253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X78.725447 Y229.548003 Z4 E17462.67052 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X79.194239 Y231.419524 Z4 E17470.691788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X79.477332 Y233.327983 Z4 E17478.713056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X79.572 Y235.255 Z4 E17486.734323 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X79.477332 Y237.182017 Z4 E17494.755591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X79.194239 Y239.090476 Z4 E17502.776858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X78.725447 Y240.961997 Z4 E17510.798126 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X78.075472 Y242.778556 Z4 E17518.819394 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X77.250572 Y244.52266 Z4 E17526.840661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X76.258693 Y246.177511 Z4 E17534.861929 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X75.109386 Y247.727172 Z4 E17542.883196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X73.813719 Y249.156719 Z4 E17550.904464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X72.384172 Y250.452386 Z4 E17558.925731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X70.834511 Y251.601693 Z4 E17566.946999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X69.17966 Y252.593572 Z4 E17574.968267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X67.435556 Y253.418472 Z4 E17582.989534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X65.618997 Y254.068447 Z4 E17591.010802 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X63.747476 Y254.537239 Z4 E17599.032069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X61.839017 Y254.820332 Z4 E17607.053337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X59.912 Y254.915 Z4 E17615.074605 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X57.984983 Y254.820332 Z4 E17623.095872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X56.076524 Y254.537239 Z4 E17631.11714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X54.205003 Y254.068447 Z4 E17639.138407 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X52.388444 Y253.418472 Z4 E17647.159675 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X50.64434 Y252.593572 Z4 E17655.180943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X48.989489 Y251.601693 Z4 E17663.20221 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X47.439828 Y250.452386 Z4 E17671.223478 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X46.010281 Y249.156719 Z4 E17679.244745 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X44.714614 Y247.727172 Z4 E17687.266013 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X43.565307 Y246.177511 Z4 E17695.28728 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X42.573428 Y244.52266 Z4 E17703.308548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X41.748528 Y242.778556 Z4 E17711.329816 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X41.098553 Y240.961997 Z4 E17719.351083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X40.629761 Y239.090476 Z4 E17727.372351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X40.346668 Y237.182017 Z4 E17735.393618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X40.252 Y235.255 Z4 E17743.414886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X40.346668 Y233.327983 Z4 E17751.436154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X40.629761 Y231.419524 Z4 E17759.457421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X41.098553 Y229.548003 Z4 E17767.478689 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X41.748528 Y227.731444 Z4 E17775.499956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X42.573428 Y225.98734 Z4 E17783.521224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X42.978553 Y225.31143 Z4 E17786.797442 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X43.565307 Y224.332489 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X44.714614 Y222.782828 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X46.010281 Y221.353281 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0000
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
