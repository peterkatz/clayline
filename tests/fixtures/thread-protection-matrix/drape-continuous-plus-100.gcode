; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=drape-job
; prepared_trace_sha256=6a4d3a0101e57d4641fbfde0a440623ecc6318373c818f701928a60c7319dac8
; body_sha256=de4a01f04789a6572ac8422d3a72921370bde229d76e89e774f87095b6f1b687
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
; stats.motion_time_seconds=59.34862
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=59.34862
; stats.body_volume_mm3=25809.089043
; stats.wet_weight_g=46.45636
; stats.body_e=10730.172337
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
; parameter.joint_boost=1.0
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
G1 X127.620382 Y204.950429 Z20 E121.99233 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z20 E146.025477 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z20 E170.058624 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z20 E194.09177 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.482736 Y212.235648 Z20 E195.918367 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z20 E207.021642 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z20 E219.038215 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z20 E231.054789 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z20 E243.071362 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z20 E255.087935 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z20 E267.104509 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z20 E279.121082 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z20 E291.137655 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z20 E303.154228 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z20 E315.170802 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z20 E327.187375 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z20 E339.203948 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z20 E351.220522 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z20 E363.237095 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z20 E375.253668 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z20 E387.270242 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z20 E399.286815 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z20 E411.303388 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z20 E423.319962 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z20 E435.336535 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z20 E447.353108 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z20 E459.369681 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z20 E471.386255 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z20 E483.402828 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z20 E495.419401 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z20 E507.435975 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z20 E519.452548 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z20 E531.469121 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z20 E543.485695 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z20 E555.502268 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z20 E567.518841 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z20 E579.535414 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z20 E591.551988 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z20 E603.568561 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z20 E615.585134 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z20 E627.601708 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z20 E639.618281 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z20 E651.634854 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z20 E663.651428 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z20 E675.668001 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z20 E687.684574 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z20 E699.701148 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z20 E711.717721 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z20 E723.734294 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z20 E735.750867 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z20 E747.767441 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z20 E759.784014 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z20 E771.800587 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z20 E783.817161 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z20 E795.833734 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z20 E807.850307 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z20 E819.866881 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z20 E831.883454 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z20 E843.900027 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z20 E855.9166 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.482736 Y192.764352 Z20 E867.019875 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z20 E868.846472 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z20 E892.879619 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z20 E916.912766 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z20 E940.945912 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z20 E964.979059 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z20 E2042.530079 F1200 ; clayline kind=carry page=0 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z20 E2066.563226 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z20 E2090.596372 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z20 E2114.629519 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z20 E2138.662666 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.482736 Y212.235648 Z20 E2140.489263 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z20 E2151.592538 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z20 E2163.609111 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z20 E2175.625684 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z20 E2187.642258 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z20 E2199.658831 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z20 E2211.675404 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z20 E2223.691977 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z20 E2235.708551 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z20 E2247.725124 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z20 E2259.741697 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z20 E2271.758271 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z20 E2283.774844 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z20 E2295.791417 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z20 E2307.807991 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z20 E2319.824564 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z20 E2331.841137 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z20 E2343.85771 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z20 E2355.874284 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z20 E2367.890857 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z20 E2379.90743 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z20 E2391.924004 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z20 E2403.940577 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z20 E2415.95715 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z20 E2427.973724 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z20 E2439.990297 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z20 E2452.00687 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z20 E2464.023444 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z20 E2476.040017 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z20 E2488.05659 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z20 E2500.073163 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z20 E2512.089737 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z20 E2524.10631 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z20 E2536.122883 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z20 E2548.139457 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z20 E2560.15603 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z20 E2572.172603 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z20 E2584.189177 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z20 E2596.20575 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z20 E2608.222323 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z20 E2620.238896 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z20 E2632.25547 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z20 E2644.272043 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z20 E2656.288616 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z20 E2668.30519 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z20 E2680.321763 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z20 E2692.338336 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z20 E2704.35491 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z20 E2716.371483 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z20 E2728.388056 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z20 E2740.40463 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z20 E2752.421203 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z20 E2764.437776 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z20 E2776.454349 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z20 E2788.470923 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z20 E2800.487496 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.482736 Y192.764352 Z20 E2811.590771 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z20 E2813.417368 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z20 E2837.450515 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z20 E2861.483661 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z20 E2885.516808 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z20 E2909.549954 F1200 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=1
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-drape page_name=drape z_mode=drape
G1 X127.5 Y202.5 Z22 E3987.279068 F1200 ; clayline kind=carry page=1 layer=0 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z22 E4011.312214 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z22 E4035.345361 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z22 E4059.378508 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z22 E4083.411654 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.482736 Y212.235648 Z22 E4085.238251 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z22 E4096.341526 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z22 E4108.358099 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z22 E4120.374673 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z22 E4132.391246 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z22 E4144.407819 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z22 E4156.424393 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z22 E4168.440966 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z22 E4180.457539 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z22 E4192.474113 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z22 E4204.490686 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z22 E4216.507259 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z22 E4228.523832 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z22 E4240.540406 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z22 E4252.556979 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z22 E4264.573552 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z22 E4276.590126 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z22 E4288.606699 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z22 E4300.623272 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z22 E4312.639846 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z22 E4324.656419 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z22 E4336.672992 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z22 E4348.689565 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z22 E4360.706139 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z22 E4372.722712 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z22 E4384.739285 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z22 E4396.755859 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z22 E4408.772432 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z22 E4420.789005 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z22 E4432.805579 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z22 E4444.822152 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z22 E4456.838725 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z22 E4468.855299 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z22 E4480.871872 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z22 E4492.888445 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z22 E4504.905018 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z22 E4516.921592 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z22 E4528.938165 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z22 E4540.954738 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z22 E4552.971312 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z22 E4564.987885 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z22 E4577.004458 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z22 E4589.021032 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z22 E4601.037605 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z22 E4613.054178 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z22 E4625.070751 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z22 E4637.087325 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z22 E4649.103898 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z22 E4661.120471 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z22 E4673.137045 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z22 E4685.153618 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z22 E4697.170191 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z22 E4709.186765 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z22 E4721.203338 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z22 E4733.219911 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z22 E4745.236485 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.482736 Y192.764352 Z22 E4756.339759 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z22 E4758.166356 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z22 E4782.199503 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z22 E4806.23265 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z22 E4830.265796 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z22 E4854.298943 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z22 E5931.849963 F1200 ; clayline kind=carry page=1 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z22 E5955.88311 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z22 E5979.916257 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z22 E6003.949403 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z22 E6027.98255 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.482736 Y212.235648 Z22 E6029.809147 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z22 E6040.912422 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z22 E6052.928995 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z22 E6064.945568 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z22 E6076.962142 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z22 E6088.978715 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z22 E6100.995288 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z22 E6113.011861 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z22 E6125.028435 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z22 E6137.045008 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z22 E6149.061581 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z22 E6161.078155 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z22 E6173.094728 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z22 E6185.111301 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z22 E6197.127875 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z22 E6209.144448 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z22 E6221.161021 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z22 E6233.177595 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z22 E6245.194168 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z22 E6257.210741 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z22 E6269.227314 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z22 E6281.243888 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z22 E6293.260461 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z22 E6305.277034 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z22 E6317.293608 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z22 E6329.310181 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z22 E6341.326754 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z22 E6353.343328 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z22 E6365.359901 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z22 E6377.376474 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z22 E6389.393048 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z22 E6401.409621 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z22 E6413.426194 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z22 E6425.442767 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z22 E6437.459341 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z22 E6449.475914 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z22 E6461.492487 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z22 E6473.509061 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z22 E6485.525634 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z22 E6497.542207 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z22 E6509.558781 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z22 E6521.575354 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z22 E6533.591927 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z22 E6545.6085 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z22 E6557.625074 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z22 E6569.641647 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z22 E6581.65822 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z22 E6593.674794 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z22 E6605.691367 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z22 E6617.70794 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z22 E6629.724514 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z22 E6641.741087 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z22 E6653.75766 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z22 E6665.774234 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z22 E6677.790807 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z22 E6689.80738 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.482736 Y192.764352 Z22 E6700.910655 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z22 E6702.737252 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z22 E6726.770399 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z22 E6750.803545 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z22 E6774.836692 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z22 E6798.869838 F1200 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=2
; CLAYLINE_MARKER page=2 layer=0 text=layer 0 page_id=page-03-drape page_name=drape z_mode=drape
G1 X127.5 Y202.5 Z24 E7876.598952 F1200 ; clayline kind=carry page=2 layer=0 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z24 E7900.632098 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z24 E7924.665245 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z24 E7948.698392 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z24 E7972.731538 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.482736 Y212.235648 Z24 E7974.558135 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z24 E7985.66141 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z24 E7997.677983 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z24 E8009.694557 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z24 E8021.71113 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z24 E8033.727703 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z24 E8045.744277 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z24 E8057.76085 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z24 E8069.777423 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z24 E8081.793997 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z24 E8093.81057 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z24 E8105.827143 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z24 E8117.843716 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z24 E8129.86029 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z24 E8141.876863 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z24 E8153.893436 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z24 E8165.91001 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z24 E8177.926583 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z24 E8189.943156 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z24 E8201.95973 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z24 E8213.976303 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z24 E8225.992876 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z24 E8238.00945 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z24 E8250.026023 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z24 E8262.042596 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z24 E8274.059169 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z24 E8286.075743 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z24 E8298.092316 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z24 E8310.108889 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z24 E8322.125463 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z24 E8334.142036 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z24 E8346.158609 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z24 E8358.175183 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z24 E8370.191756 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z24 E8382.208329 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z24 E8394.224902 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z24 E8406.241476 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z24 E8418.258049 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z24 E8430.274622 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z24 E8442.291196 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z24 E8454.307769 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z24 E8466.324342 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z24 E8478.340916 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z24 E8490.357489 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z24 E8502.374062 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z24 E8514.390636 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z24 E8526.407209 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z24 E8538.423782 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z24 E8550.440355 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z24 E8562.456929 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z24 E8574.473502 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z24 E8586.490075 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z24 E8598.506649 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z24 E8610.523222 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z24 E8622.539795 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z24 E8634.556369 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.482736 Y192.764352 Z24 E8645.659643 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z24 E8647.486241 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z24 E8671.519387 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z24 E8695.552534 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z24 E8719.58568 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z24 E8743.618827 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z24 E9821.169847 F1200 ; clayline kind=carry page=2 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z24 E9845.202994 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z24 E9869.236141 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z24 E9893.269287 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z24 E9917.302434 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.482736 Y212.235648 Z24 E9919.129031 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z24 E9930.232306 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z24 E9942.248879 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z24 E9954.265452 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z24 E9966.282026 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z24 E9978.298599 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z24 E9990.315172 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z24 E10002.331746 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z24 E10014.348319 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z24 E10026.364892 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z24 E10038.381465 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z24 E10050.398039 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z24 E10062.414612 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z24 E10074.431185 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z24 E10086.447759 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z24 E10098.464332 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z24 E10110.480905 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z24 E10122.497479 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z24 E10134.514052 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z24 E10146.530625 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z24 E10158.547199 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z24 E10170.563772 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z24 E10182.580345 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z24 E10194.596918 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z24 E10206.613492 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z24 E10218.630065 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z24 E10230.646638 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z24 E10242.663212 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z24 E10254.679785 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z24 E10266.696358 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z24 E10278.712932 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z24 E10290.729505 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z24 E10302.746078 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z24 E10314.762651 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z24 E10326.779225 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z24 E10338.795798 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z24 E10350.812371 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z24 E10362.828945 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z24 E10374.845518 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z24 E10386.862091 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z24 E10398.878665 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z24 E10410.895238 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z24 E10422.911811 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z24 E10434.928385 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z24 E10446.944958 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z24 E10458.961531 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z24 E10470.978104 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z24 E10482.994678 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z24 E10495.011251 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z24 E10507.027824 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z24 E10519.044398 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z24 E10531.060971 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z24 E10543.077544 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z24 E10555.094118 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z24 E10567.110691 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z24 E10579.127264 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.482736 Y192.764352 Z24 E10590.230539 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z24 E10592.057136 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z24 E10616.090283 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z24 E10640.123429 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z24 E10664.156576 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z24 E10688.189723 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.549068 Y203.498795 Z24 E10692.597886 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z24 E10696.516253 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z24 E10698.192096 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z24 E10700.066209 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z24 E10703.004985 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z24 E10705.267047 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z24 E10705.495372 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z24 E10707.454555 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z24 E10708.923943 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z24 E10709.389614 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z24 E10710.016405 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z24 E10710.506201 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z24 E10710.580501 F1200 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.482736 Y212.235648 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X240.451968 Y214.284918 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X241.71326 Y216.389256 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X243.174739 Y218.359832 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X244.82233 Y220.17767 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X245.098654 Y220.428114 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0001
G1 X245.098654 Y220.428114 Z26 E10730.172337 F1200 ; clayline kind=thread_release page=2 layer=0 stroke=stroke-0001 note=thread release
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
