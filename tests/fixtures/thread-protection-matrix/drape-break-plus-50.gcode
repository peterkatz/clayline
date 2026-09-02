; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=drape-job
; prepared_trace_sha256=21e404bfec80654420529e1c39c81d0448d7d03475dde77950e730ba1f970f67
; body_sha256=3aff96532bb7b64d7daa788fb5695f49f22d010c7f2b9f5192ee505f65ec8f2e
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
; stats.motion_count=466
; stats.print_motion_count=459
; stats.travel_motion_count=7
; stats.stroke_count=6
; stats.page_count=3
; stats.print_path_mm=1338.099347
; stats.deposited_path_mm=1307.539952
; stats.travel_path_mm=333.91478
; stats.total_motion_path_mm=1672.014127
; stats.motion_time_seconds=55.215299
; stats.pause_time_seconds=4
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=59.215299
; stats.body_volume_mm3=18571.349562
; stats.wet_weight_g=33.428429
; stats.body_e=7721.06993
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
; parameter.page_pause_seconds=2.0
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
G1 X237.549068 Y203.498795 Z20 E2545.509138 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z20 E2548.447914 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z20 E2549.704796 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z20 E2551.110381 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z20 E2553.314462 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z20 E2555.011009 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z20 E2555.182253 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z20 E2556.65164 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z20 E2557.753681 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z20 E2558.102934 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z20 E2558.573027 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z20 E2558.940374 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z20 E2558.996099 F1600 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.482736 Y212.235648 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X240.451968 Y214.284918 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X241.71326 Y216.389256 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X243.174739 Y218.359832 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X244.82233 Y220.17767 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X245.098654 Y220.428114 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
G1 X245.098654 Y220.428114 Z22 E2573.689977 F1600 ; clayline kind=thread_release page=0 layer=0 stroke=stroke-0001 note=thread release
; CLAYLINE_PAGE index=1
G0 X245.098654 Y220.428114 Z26 F2400 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0000 note=inter-page clearance above completed material
G0 X127.5 Y202.5 Z26 F2400 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0000 note=inter-page XY within common stack footprint
G4 S2
G0 X127.5 Y202.5 Z22 F2400 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0000 note=inter-page approach
G1 E2671.64916 F2400 ; clayline kind=thread_launch page=1 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-drape page_name=drape z_mode=drape
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z22 E2689.67402 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z22 E2707.69888 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z22 E2725.72374 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z22 E2743.7486 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.482736 Y212.235648 Z22 E2745.118548 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z22 E2756.221823 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z22 E2768.238396 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z22 E2780.25497 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z22 E2792.271543 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z22 E2804.288116 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z22 E2816.304689 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z22 E2828.321263 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z22 E2840.337836 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z22 E2852.354409 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z22 E2864.370983 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z22 E2876.387556 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z22 E2888.404129 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z22 E2900.420703 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z22 E2912.437276 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z22 E2924.453849 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z22 E2936.470422 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z22 E2948.486996 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z22 E2960.503569 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z22 E2972.520142 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z22 E2984.536716 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z22 E2996.553289 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z22 E3008.569862 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z22 E3020.586436 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z22 E3032.603009 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z22 E3044.619582 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z22 E3056.636156 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z22 E3068.652729 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z22 E3080.669302 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z22 E3092.685875 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z22 E3104.702449 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z22 E3116.719022 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z22 E3128.735595 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z22 E3140.752169 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z22 E3152.768742 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z22 E3164.785315 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z22 E3176.801889 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z22 E3188.818462 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z22 E3200.835035 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z22 E3212.851608 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z22 E3224.868182 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z22 E3236.884755 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z22 E3248.901328 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z22 E3260.917902 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z22 E3272.934475 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z22 E3284.951048 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z22 E3296.967622 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z22 E3308.984195 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z22 E3321.000768 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z22 E3333.017342 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z22 E3345.033915 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z22 E3357.050488 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z22 E3369.067061 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z22 E3381.083635 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z22 E3393.100208 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z22 E3405.116781 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.482736 Y192.764352 Z22 E3416.220056 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z22 E3417.590004 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z22 E3435.614864 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z22 E3453.639724 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z22 E3471.664584 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z22 E3489.689444 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z22 E4297.852709 F1600 ; clayline kind=carry page=1 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z22 E4315.877569 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z22 E4333.902429 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z22 E4351.927289 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z22 E4369.952149 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.482736 Y212.235648 Z22 E4371.322097 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z22 E4382.425372 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z22 E4394.441945 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z22 E4406.458518 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z22 E4418.475091 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z22 E4430.491665 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z22 E4442.508238 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z22 E4454.524811 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z22 E4466.541385 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z22 E4478.557958 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z22 E4490.574531 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z22 E4502.591105 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z22 E4514.607678 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z22 E4526.624251 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z22 E4538.640825 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z22 E4550.657398 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z22 E4562.673971 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z22 E4574.690544 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z22 E4586.707118 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z22 E4598.723691 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z22 E4610.740264 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z22 E4622.756838 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z22 E4634.773411 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z22 E4646.789984 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z22 E4658.806558 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z22 E4670.823131 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z22 E4682.839704 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z22 E4694.856277 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z22 E4706.872851 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z22 E4718.889424 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z22 E4730.905997 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z22 E4742.922571 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z22 E4754.939144 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z22 E4766.955717 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z22 E4778.972291 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z22 E4790.988864 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z22 E4803.005437 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z22 E4815.022011 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z22 E4827.038584 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z22 E4839.055157 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z22 E4851.07173 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z22 E4863.088304 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z22 E4875.104877 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z22 E4887.12145 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z22 E4899.138024 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z22 E4911.154597 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z22 E4923.17117 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z22 E4935.187744 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z22 E4947.204317 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z22 E4959.22089 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z22 E4971.237463 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z22 E4983.254037 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z22 E4995.27061 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z22 E5007.287183 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z22 E5019.303757 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z22 E5031.32033 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.482736 Y192.764352 Z22 E5042.423605 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z22 E5043.793553 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z22 E5061.818413 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z22 E5079.843273 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z22 E5097.868133 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z22 E5115.892992 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.549068 Y203.498795 Z22 E5119.199115 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z22 E5122.13789 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z22 E5123.394773 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z22 E5124.800357 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z22 E5127.004439 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z22 E5128.700986 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z22 E5128.872229 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z22 E5130.341617 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z22 E5131.443658 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z22 E5131.792911 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z22 E5132.263004 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z22 E5132.630351 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z22 E5132.686076 F1600 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.482736 Y212.235648 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X240.451968 Y214.284918 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X241.71326 Y216.389256 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X243.174739 Y218.359832 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X244.82233 Y220.17767 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X245.098654 Y220.428114 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
G1 X245.098654 Y220.428114 Z24 E5147.379954 F1600 ; clayline kind=thread_release page=1 layer=0 stroke=stroke-0001 note=thread release
; CLAYLINE_PAGE index=2
G0 X245.098654 Y220.428114 Z28 F2400 ; clayline kind=travel_lift page=2 layer=0 stroke=stroke-0000 note=inter-page clearance above completed material
G0 X127.5 Y202.5 Z28 F2400 ; clayline kind=travel_xy page=2 layer=0 stroke=stroke-0000 note=inter-page XY within common stack footprint
G4 S2
G0 X127.5 Y202.5 Z24 F2400 ; clayline kind=travel_approach page=2 layer=0 stroke=stroke-0000 note=inter-page approach
G1 E5245.339137 F2400 ; clayline kind=thread_launch page=2 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=2 layer=0 text=layer 0 page_id=page-03-drape page_name=drape z_mode=drape
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z24 E5263.363997 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z24 E5281.388857 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z24 E5299.413717 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z24 E5317.438577 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.482736 Y212.235648 Z24 E5318.808525 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z24 E5329.9118 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z24 E5341.928373 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z24 E5353.944946 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z24 E5365.96152 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z24 E5377.978093 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z24 E5389.994666 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z24 E5402.01124 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z24 E5414.027813 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z24 E5426.044386 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z24 E5438.060959 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z24 E5450.077533 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z24 E5462.094106 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z24 E5474.110679 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z24 E5486.127253 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z24 E5498.143826 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z24 E5510.160399 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z24 E5522.176973 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z24 E5534.193546 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z24 E5546.210119 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z24 E5558.226693 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z24 E5570.243266 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z24 E5582.259839 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z24 E5594.276412 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z24 E5606.292986 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z24 E5618.309559 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z24 E5630.326132 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z24 E5642.342706 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z24 E5654.359279 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z24 E5666.375852 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z24 E5678.392426 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z24 E5690.408999 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z24 E5702.425572 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z24 E5714.442145 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z24 E5726.458719 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z24 E5738.475292 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z24 E5750.491865 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z24 E5762.508439 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z24 E5774.525012 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z24 E5786.541585 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z24 E5798.558159 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z24 E5810.574732 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z24 E5822.591305 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z24 E5834.607879 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z24 E5846.624452 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z24 E5858.641025 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z24 E5870.657598 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z24 E5882.674172 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z24 E5894.690745 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z24 E5906.707318 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z24 E5918.723892 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z24 E5930.740465 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z24 E5942.757038 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z24 E5954.773612 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z24 E5966.790185 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z24 E5978.806758 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.482736 Y192.764352 Z24 E5989.910033 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z24 E5991.279981 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z24 E6009.304841 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z24 E6027.329701 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z24 E6045.354561 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z24 E6063.379421 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z24 E6871.542686 F1600 ; clayline kind=carry page=2 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z24 E6889.567546 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z24 E6907.592406 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z24 E6925.617266 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z24 E6943.642126 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.482736 Y212.235648 Z24 E6945.012074 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z24 E6956.115348 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z24 E6968.131922 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z24 E6980.148495 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z24 E6992.165068 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z24 E7004.181642 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z24 E7016.198215 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z24 E7028.214788 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z24 E7040.231362 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z24 E7052.247935 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z24 E7064.264508 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z24 E7076.281081 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z24 E7088.297655 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z24 E7100.314228 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z24 E7112.330801 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z24 E7124.347375 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z24 E7136.363948 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z24 E7148.380521 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z24 E7160.397095 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z24 E7172.413668 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z24 E7184.430241 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z24 E7196.446814 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z24 E7208.463388 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z24 E7220.479961 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z24 E7232.496534 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z24 E7244.513108 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z24 E7256.529681 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z24 E7268.546254 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z24 E7280.562828 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z24 E7292.579401 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z24 E7304.595974 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z24 E7316.612548 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z24 E7328.629121 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z24 E7340.645694 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z24 E7352.662267 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z24 E7364.678841 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z24 E7376.695414 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z24 E7388.711987 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z24 E7400.728561 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z24 E7412.745134 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z24 E7424.761707 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z24 E7436.778281 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z24 E7448.794854 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z24 E7460.811427 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z24 E7472.828 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z24 E7484.844574 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z24 E7496.861147 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z24 E7508.87772 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z24 E7520.894294 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z24 E7532.910867 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z24 E7544.92744 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z24 E7556.944014 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z24 E7568.960587 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z24 E7580.97716 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z24 E7592.993734 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z24 E7605.010307 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.482736 Y192.764352 Z24 E7616.113582 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z24 E7617.483529 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z24 E7635.508389 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z24 E7653.533249 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z24 E7671.558109 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z24 E7689.582969 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.549068 Y203.498795 Z24 E7692.889092 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z24 E7695.827867 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z24 E7697.08475 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z24 E7698.490334 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z24 E7700.694416 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z24 E7702.390963 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z24 E7702.562206 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z24 E7704.031594 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z24 E7705.133635 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z24 E7705.482888 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z24 E7705.952981 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z24 E7706.320328 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z24 E7706.376053 F1600 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.482736 Y212.235648 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X240.451968 Y214.284918 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X241.71326 Y216.389256 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X243.174739 Y218.359832 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X244.82233 Y220.17767 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X245.098654 Y220.428114 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0001
G1 X245.098654 Y220.428114 Z26 E7721.06993 F1600 ; clayline kind=thread_release page=2 layer=0 stroke=stroke-0001 note=thread release
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
