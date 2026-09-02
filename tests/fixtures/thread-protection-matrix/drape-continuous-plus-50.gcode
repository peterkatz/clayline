; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=drape-job
; prepared_trace_sha256=bff580c5d1dbe3d9789ca87f6e2cd4d1398d7a1858bff6b570155a9a2f37825c
; body_sha256=0e9771a934b791a094ea5e9c00cedeba63ad5e369c68fec9dce5475e10387245
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
; stats.motion_count=422
; stats.print_motion_count=421
; stats.travel_motion_count=1
; stats.stroke_count=6
; stats.page_count=3
; stats.print_path_mm=1514.135708
; stats.deposited_path_mm=1503.949243
; stats.travel_path_mm=80
; stats.total_motion_path_mm=1594.135708
; stats.motion_time_seconds=50.825496
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=50.825496
; stats.body_volume_mm3=21837.004085
; stats.wet_weight_g=39.306607
; stats.body_e=9078.771311
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=nominal — drape mode: physical bead placement depends on fall
; parameter.alternate=false
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
; parameter.page_pause_seconds=disabled
; parameter.page_travel_clearance=50.0
; parameter.page_travel_lift=4.0
; parameter.pass_model=explicit-passes
; parameter.provisional_flow_multiplier=1.0
; parameter.stack_job_page_count=3
; parameter.stack_page_0_path_start_z_mm=20.0
; parameter.stack_page_0_z_max_mm=20.0
; parameter.stack_page_0_z_min_mm=20.0
; parameter.stack_page_1_path_start_z_mm=22.0
; parameter.stack_page_1_z_max_mm=22.0
; parameter.stack_page_1_z_min_mm=22.0
; parameter.stack_page_2_path_start_z_mm=24.0
; parameter.stack_page_2_z_max_mm=24.0
; parameter.stack_page_2_z_min_mm=24.0
; parameter.stack_page_material_height_mm=2.0
; parameter.stack_total_height_mm=6.0
; parameter.standoff_z=20.0
; parameter.thread_protection_model=extra-clay-slowdown-v1
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
G0 X127.5 Y202.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=thread launch position
G1 E97.959184 F2400 ; clayline kind=thread_launch page=0 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-01-drape page_name=drape z_mode=drape
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z20 E115.984044 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z20 E134.008904 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z20 E152.033764 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z20 E170.058624 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.482736 Y212.235648 Z20 E171.428571 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z20 E182.531846 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z20 E194.548419 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z20 E206.564993 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z20 E218.581566 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z20 E230.598139 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z20 E242.614713 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z20 E254.631286 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z20 E266.647859 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z20 E278.664433 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z20 E290.681006 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z20 E302.697579 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z20 E314.714152 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z20 E326.730726 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z20 E338.747299 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z20 E350.763872 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z20 E362.780446 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z20 E374.797019 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z20 E386.813592 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z20 E398.830166 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z20 E410.846739 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z20 E422.863312 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z20 E434.879886 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z20 E446.896459 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z20 E458.913032 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z20 E470.929605 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z20 E482.946179 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z20 E494.962752 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z20 E506.979325 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z20 E518.995899 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z20 E531.012472 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z20 E543.029045 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z20 E555.045619 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z20 E567.062192 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z20 E579.078765 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z20 E591.095338 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z20 E603.111912 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z20 E615.128485 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z20 E627.145058 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z20 E639.161632 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z20 E651.178205 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z20 E663.194778 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z20 E675.211352 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z20 E687.227925 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z20 E699.244498 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z20 E711.261072 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z20 E723.277645 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z20 E735.294218 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z20 E747.310791 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z20 E759.327365 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z20 E771.343938 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z20 E783.360511 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z20 E795.377085 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z20 E807.393658 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z20 E819.410231 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z20 E831.426805 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.482736 Y192.764352 Z20 E842.530079 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z20 E843.900027 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z20 E861.924887 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z20 E879.949747 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z20 E897.974607 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z20 E915.999467 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z20 E1724.162732 F1600 ; clayline kind=carry page=0 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z20 E1742.187592 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z20 E1760.212452 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z20 E1778.237312 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z20 E1796.262172 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.482736 Y212.235648 Z20 E1797.63212 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z20 E1808.735395 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z20 E1820.751968 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z20 E1832.768541 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z20 E1844.785115 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z20 E1856.801688 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z20 E1868.818261 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z20 E1880.834835 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z20 E1892.851408 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z20 E1904.867981 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z20 E1916.884554 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z20 E1928.901128 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z20 E1940.917701 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z20 E1952.934274 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z20 E1964.950848 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z20 E1976.967421 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z20 E1988.983994 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z20 E2001.000568 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z20 E2013.017141 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z20 E2025.033714 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z20 E2037.050288 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z20 E2049.066861 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z20 E2061.083434 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z20 E2073.100007 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z20 E2085.116581 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z20 E2097.133154 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z20 E2109.149727 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z20 E2121.166301 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z20 E2133.182874 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z20 E2145.199447 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z20 E2157.216021 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z20 E2169.232594 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z20 E2181.249167 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z20 E2193.265741 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z20 E2205.282314 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z20 E2217.298887 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z20 E2229.31546 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z20 E2241.332034 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z20 E2253.348607 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z20 E2265.36518 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z20 E2277.381754 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z20 E2289.398327 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z20 E2301.4149 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z20 E2313.431474 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z20 E2325.448047 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z20 E2337.46462 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z20 E2349.481193 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z20 E2361.497767 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z20 E2373.51434 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z20 E2385.530913 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z20 E2397.547487 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z20 E2409.56406 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z20 E2421.580633 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z20 E2433.597207 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z20 E2445.61378 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z20 E2457.630353 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.482736 Y192.764352 Z20 E2468.733628 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z20 E2470.103576 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z20 E2488.128436 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z20 E2506.153296 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z20 E2524.178156 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z20 E2542.203016 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=1
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-drape page_name=drape z_mode=drape
G1 X127.5 Y202.5 Z22 E3350.499851 F1600 ; clayline kind=carry page=1 layer=0 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z22 E3368.524711 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z22 E3386.549571 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z22 E3404.57443 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z22 E3422.59929 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.482736 Y212.235648 Z22 E3423.969238 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z22 E3435.072513 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z22 E3447.089086 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z22 E3459.10566 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z22 E3471.122233 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z22 E3483.138806 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z22 E3495.15538 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z22 E3507.171953 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z22 E3519.188526 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z22 E3531.2051 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z22 E3543.221673 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z22 E3555.238246 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z22 E3567.254819 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z22 E3579.271393 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z22 E3591.287966 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z22 E3603.304539 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z22 E3615.321113 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z22 E3627.337686 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z22 E3639.354259 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z22 E3651.370833 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z22 E3663.387406 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z22 E3675.403979 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z22 E3687.420552 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z22 E3699.437126 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z22 E3711.453699 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z22 E3723.470272 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z22 E3735.486846 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z22 E3747.503419 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z22 E3759.519992 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z22 E3771.536566 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z22 E3783.553139 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z22 E3795.569712 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z22 E3807.586286 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z22 E3819.602859 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z22 E3831.619432 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z22 E3843.636005 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z22 E3855.652579 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z22 E3867.669152 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z22 E3879.685725 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z22 E3891.702299 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z22 E3903.718872 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z22 E3915.735445 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z22 E3927.752019 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z22 E3939.768592 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z22 E3951.785165 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z22 E3963.801738 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z22 E3975.818312 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z22 E3987.834885 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z22 E3999.851458 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z22 E4011.868032 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z22 E4023.884605 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z22 E4035.901178 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z22 E4047.917752 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z22 E4059.934325 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z22 E4071.950898 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z22 E4083.967472 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.482736 Y192.764352 Z22 E4095.070746 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z22 E4096.440694 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z22 E4114.465554 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z22 E4132.490414 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z22 E4150.515274 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z22 E4168.540134 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z22 E4976.703399 F1600 ; clayline kind=carry page=1 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z22 E4994.728259 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z22 E5012.753119 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z22 E5030.777979 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z22 E5048.802839 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.482736 Y212.235648 Z22 E5050.172787 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z22 E5061.276062 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z22 E5073.292635 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z22 E5085.309208 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z22 E5097.325782 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z22 E5109.342355 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z22 E5121.358928 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z22 E5133.375502 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z22 E5145.392075 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z22 E5157.408648 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z22 E5169.425221 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z22 E5181.441795 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z22 E5193.458368 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z22 E5205.474941 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z22 E5217.491515 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z22 E5229.508088 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z22 E5241.524661 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z22 E5253.541235 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z22 E5265.557808 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z22 E5277.574381 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z22 E5289.590954 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z22 E5301.607528 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z22 E5313.624101 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z22 E5325.640674 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z22 E5337.657248 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z22 E5349.673821 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z22 E5361.690394 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z22 E5373.706968 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z22 E5385.723541 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z22 E5397.740114 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z22 E5409.756688 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z22 E5421.773261 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z22 E5433.789834 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z22 E5445.806407 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z22 E5457.822981 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z22 E5469.839554 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z22 E5481.856127 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z22 E5493.872701 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z22 E5505.889274 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z22 E5517.905847 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z22 E5529.922421 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z22 E5541.938994 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z22 E5553.955567 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z22 E5565.972141 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z22 E5577.988714 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z22 E5590.005287 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z22 E5602.02186 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z22 E5614.038434 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z22 E5626.055007 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z22 E5638.07158 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z22 E5650.088154 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z22 E5662.104727 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z22 E5674.1213 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z22 E5686.137874 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z22 E5698.154447 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z22 E5710.17102 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.482736 Y192.764352 Z22 E5721.274295 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z22 E5722.644243 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z22 E5740.669103 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z22 E5758.693963 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z22 E5776.718823 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z22 E5794.743683 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=2
; CLAYLINE_MARKER page=2 layer=0 text=layer 0 page_id=page-03-drape page_name=drape z_mode=drape
G1 X127.5 Y202.5 Z24 E6603.040518 F1600 ; clayline kind=carry page=2 layer=0 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z24 E6621.065378 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z24 E6639.090237 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z24 E6657.115097 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z24 E6675.139957 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.482736 Y212.235648 Z24 E6676.509905 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z24 E6687.61318 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z24 E6699.629753 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z24 E6711.646327 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z24 E6723.6629 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z24 E6735.679473 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z24 E6747.696047 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z24 E6759.71262 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z24 E6771.729193 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z24 E6783.745766 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z24 E6795.76234 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z24 E6807.778913 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z24 E6819.795486 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z24 E6831.81206 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z24 E6843.828633 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z24 E6855.845206 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z24 E6867.86178 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z24 E6879.878353 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z24 E6891.894926 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z24 E6903.9115 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z24 E6915.928073 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z24 E6927.944646 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z24 E6939.961219 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z24 E6951.977793 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z24 E6963.994366 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z24 E6976.010939 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z24 E6988.027513 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z24 E7000.044086 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z24 E7012.060659 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z24 E7024.077233 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z24 E7036.093806 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z24 E7048.110379 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z24 E7060.126952 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z24 E7072.143526 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z24 E7084.160099 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z24 E7096.176672 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z24 E7108.193246 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z24 E7120.209819 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z24 E7132.226392 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z24 E7144.242966 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z24 E7156.259539 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z24 E7168.276112 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z24 E7180.292686 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z24 E7192.309259 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z24 E7204.325832 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z24 E7216.342405 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z24 E7228.358979 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z24 E7240.375552 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z24 E7252.392125 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z24 E7264.408699 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z24 E7276.425272 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z24 E7288.441845 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z24 E7300.458419 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z24 E7312.474992 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z24 E7324.491565 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z24 E7336.508138 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.482736 Y192.764352 Z24 E7347.611413 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z24 E7348.981361 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z24 E7367.006221 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z24 E7385.031081 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z24 E7403.055941 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z24 E7421.080801 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z24 E8229.244066 F1600 ; clayline kind=carry page=2 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z24 E8247.268926 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z24 E8265.293786 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z24 E8283.318646 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z24 E8301.343506 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.482736 Y212.235648 Z24 E8302.713454 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z24 E8313.816729 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z24 E8325.833302 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z24 E8337.849875 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z24 E8349.866449 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z24 E8361.883022 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z24 E8373.899595 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z24 E8385.916168 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z24 E8397.932742 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z24 E8409.949315 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z24 E8421.965888 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z24 E8433.982462 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z24 E8445.999035 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z24 E8458.015608 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z24 E8470.032182 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z24 E8482.048755 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z24 E8494.065328 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z24 E8506.081902 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z24 E8518.098475 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z24 E8530.115048 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z24 E8542.131621 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z24 E8554.148195 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z24 E8566.164768 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z24 E8578.181341 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z24 E8590.197915 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z24 E8602.214488 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z24 E8614.231061 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z24 E8626.247635 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z24 E8638.264208 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z24 E8650.280781 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z24 E8662.297354 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z24 E8674.313928 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z24 E8686.330501 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z24 E8698.347074 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z24 E8710.363648 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z24 E8722.380221 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z24 E8734.396794 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z24 E8746.413368 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z24 E8758.429941 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z24 E8770.446514 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z24 E8782.463088 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z24 E8794.479661 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z24 E8806.496234 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z24 E8818.512807 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z24 E8830.529381 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z24 E8842.545954 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z24 E8854.562527 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z24 E8866.579101 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z24 E8878.595674 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z24 E8890.612247 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z24 E8902.628821 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z24 E8914.645394 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z24 E8926.661967 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z24 E8938.678541 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z24 E8950.695114 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z24 E8962.711687 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.482736 Y192.764352 Z24 E8973.814962 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z24 E8975.18491 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z24 E8993.20977 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z24 E9011.23463 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z24 E9029.25949 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z24 E9047.28435 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.549068 Y203.498795 Z24 E9050.590472 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z24 E9053.529248 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z24 E9054.78613 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z24 E9056.191715 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z24 E9058.395796 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z24 E9060.092343 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z24 E9060.263586 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z24 E9061.732974 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z24 E9062.835015 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z24 E9063.184268 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z24 E9063.654361 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z24 E9064.021708 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z24 E9064.077433 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.482736 Y212.235648 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X240.451968 Y214.284918 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X241.71326 Y216.389256 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X243.174739 Y218.359832 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X244.82233 Y220.17767 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X245.098654 Y220.428114 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0001
G1 X245.098654 Y220.428114 Z26 E9078.771311 F1600 ; clayline kind=thread_release page=2 layer=0 stroke=stroke-0001 note=thread release
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
