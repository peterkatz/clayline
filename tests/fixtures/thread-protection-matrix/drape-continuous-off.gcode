; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=drape-job
; prepared_trace_sha256=4b1ccf11aa3c446159c8d98497f5c5a33d84bfc71dedeaa5578eaf0a13aea748
; body_sha256=f98a13a42fd2e566ea765d09cab0e6460041b4241e09c573f36a86d6507cdeec
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
; stats.motion_count=409
; stats.print_motion_count=408
; stats.travel_motion_count=1
; stats.stroke_count=6
; stats.page_count=3
; stats.print_path_mm=1512.135708
; stats.deposited_path_mm=1501.949243
; stats.travel_path_mm=80
; stats.total_motion_path_mm=1592.135708
; stats.motion_time_seconds=42.252372
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=42.252372
; stats.body_volume_mm3=17841.357181
; stats.wet_weight_g=32.114443
; stats.body_e=7417.574366
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
; parameter.joint_boost=0.0
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
G1 X127.620382 Y204.950429 Z20 E109.975757 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z20 E121.99233 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z20 E134.008904 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z20 E146.025477 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z20 E158.04205 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z20 E170.058624 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z20 E182.075197 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z20 E194.09177 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z20 E206.108343 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z20 E218.124917 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z20 E230.14149 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z20 E242.158063 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z20 E254.174637 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z20 E266.19121 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z20 E278.207783 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z20 E290.224357 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z20 E302.24093 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z20 E314.257503 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z20 E326.274076 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z20 E338.29065 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z20 E350.307223 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z20 E362.323796 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z20 E374.34037 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z20 E386.356943 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z20 E398.373516 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z20 E410.39009 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z20 E422.406663 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z20 E434.423236 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z20 E446.43981 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z20 E458.456383 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z20 E470.472956 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z20 E482.489529 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z20 E494.506103 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z20 E506.522676 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z20 E518.539249 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z20 E530.555823 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z20 E542.572396 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z20 E554.588969 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z20 E566.605543 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z20 E578.622116 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z20 E590.638689 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z20 E602.655262 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z20 E614.671836 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z20 E626.688409 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z20 E638.704982 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z20 E650.721556 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z20 E662.738129 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z20 E674.754702 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z20 E686.771276 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z20 E698.787849 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z20 E710.804422 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z20 E722.820996 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z20 E734.837569 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z20 E746.854142 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z20 E758.870715 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z20 E770.887289 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z20 E782.903862 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z20 E794.920435 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z20 E806.937009 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z20 E818.953582 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z20 E830.970155 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z20 E842.986729 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z20 E855.003302 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z20 E867.019875 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z20 E1405.795385 F2400 ; clayline kind=carry page=0 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z20 E1417.811959 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z20 E1429.828532 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z20 E1441.845105 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z20 E1453.861679 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z20 E1465.878252 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z20 E1477.894825 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z20 E1489.911399 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z20 E1501.927972 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z20 E1513.944545 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z20 E1525.961118 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z20 E1537.977692 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z20 E1549.994265 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z20 E1562.010838 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z20 E1574.027412 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z20 E1586.043985 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z20 E1598.060558 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z20 E1610.077132 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z20 E1622.093705 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z20 E1634.110278 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z20 E1646.126851 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z20 E1658.143425 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z20 E1670.159998 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z20 E1682.176571 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z20 E1694.193145 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z20 E1706.209718 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z20 E1718.226291 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z20 E1730.242865 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z20 E1742.259438 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z20 E1754.276011 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z20 E1766.292585 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z20 E1778.309158 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z20 E1790.325731 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z20 E1802.342304 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z20 E1814.358878 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z20 E1826.375451 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z20 E1838.392024 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z20 E1850.408598 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z20 E1862.425171 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z20 E1874.441744 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z20 E1886.458318 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z20 E1898.474891 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z20 E1910.491464 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z20 E1922.508037 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z20 E1934.524611 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z20 E1946.541184 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z20 E1958.557757 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z20 E1970.574331 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z20 E1982.590904 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z20 E1994.607477 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z20 E2006.624051 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z20 E2018.640624 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z20 E2030.657197 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z20 E2042.673771 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z20 E2054.690344 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z20 E2066.706917 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z20 E2078.72349 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z20 E2090.740064 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z20 E2102.756637 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z20 E2114.77321 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z20 E2126.789784 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z20 E2138.806357 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z20 E2150.82293 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z20 E2162.839504 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z20 E2174.856077 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=1
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-drape page_name=drape z_mode=drape
G1 X127.5 Y202.5 Z22 E2713.720634 F2400 ; clayline kind=carry page=1 layer=0 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z22 E2725.737207 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z22 E2737.75378 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z22 E2749.770353 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z22 E2761.786927 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z22 E2773.8035 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z22 E2785.820073 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z22 E2797.836647 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z22 E2809.85322 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z22 E2821.869793 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z22 E2833.886367 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z22 E2845.90294 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z22 E2857.919513 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z22 E2869.936086 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z22 E2881.95266 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z22 E2893.969233 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z22 E2905.985806 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z22 E2918.00238 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z22 E2930.018953 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z22 E2942.035526 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z22 E2954.0521 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z22 E2966.068673 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z22 E2978.085246 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z22 E2990.10182 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z22 E3002.118393 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z22 E3014.134966 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z22 E3026.151539 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z22 E3038.168113 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z22 E3050.184686 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z22 E3062.201259 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z22 E3074.217833 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z22 E3086.234406 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z22 E3098.250979 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z22 E3110.267553 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z22 E3122.284126 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z22 E3134.300699 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z22 E3146.317272 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z22 E3158.333846 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z22 E3170.350419 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z22 E3182.366992 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z22 E3194.383566 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z22 E3206.400139 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z22 E3218.416712 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z22 E3230.433286 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z22 E3242.449859 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z22 E3254.466432 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z22 E3266.483006 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z22 E3278.499579 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z22 E3290.516152 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z22 E3302.532725 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z22 E3314.549299 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z22 E3326.565872 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z22 E3338.582445 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z22 E3350.599019 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z22 E3362.615592 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z22 E3374.632165 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z22 E3386.648739 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z22 E3398.665312 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z22 E3410.681885 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z22 E3422.698459 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z22 E3434.715032 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z22 E3446.731605 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z22 E3458.748178 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z22 E3470.764752 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z22 E3482.781325 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z22 E4021.556835 F2400 ; clayline kind=carry page=1 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z22 E4033.573409 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z22 E4045.589982 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z22 E4057.606555 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z22 E4069.623128 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z22 E4081.639702 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z22 E4093.656275 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z22 E4105.672848 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z22 E4117.689422 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z22 E4129.705995 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z22 E4141.722568 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z22 E4153.739142 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z22 E4165.755715 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z22 E4177.772288 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z22 E4189.788861 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z22 E4201.805435 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z22 E4213.822008 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z22 E4225.838581 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z22 E4237.855155 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z22 E4249.871728 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z22 E4261.888301 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z22 E4273.904875 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z22 E4285.921448 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z22 E4297.938021 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z22 E4309.954595 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z22 E4321.971168 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z22 E4333.987741 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z22 E4346.004314 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z22 E4358.020888 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z22 E4370.037461 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z22 E4382.054034 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z22 E4394.070608 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z22 E4406.087181 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z22 E4418.103754 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z22 E4430.120328 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z22 E4442.136901 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z22 E4454.153474 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z22 E4466.170048 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z22 E4478.186621 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z22 E4490.203194 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z22 E4502.219767 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z22 E4514.236341 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z22 E4526.252914 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z22 E4538.269487 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z22 E4550.286061 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z22 E4562.302634 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z22 E4574.319207 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z22 E4586.335781 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z22 E4598.352354 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z22 E4610.368927 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z22 E4622.3855 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z22 E4634.402074 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z22 E4646.418647 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z22 E4658.43522 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z22 E4670.451794 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z22 E4682.468367 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z22 E4694.48494 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z22 E4706.501514 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z22 E4718.518087 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z22 E4730.53466 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z22 E4742.551234 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z22 E4754.567807 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z22 E4766.58438 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z22 E4778.600953 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z22 E4790.617527 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=2
; CLAYLINE_MARKER page=2 layer=0 text=layer 0 page_id=page-03-drape page_name=drape z_mode=drape
G1 X127.5 Y202.5 Z24 E5329.482083 F2400 ; clayline kind=carry page=2 layer=0 stroke=stroke-0000 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z24 E5341.498657 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z24 E5353.51523 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z24 E5365.531803 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z24 E5377.548377 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z24 E5389.56495 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z24 E5401.581523 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z24 E5413.598097 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z24 E5425.61467 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z24 E5437.631243 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z24 E5449.647816 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z24 E5461.66439 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z24 E5473.680963 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z24 E5485.697536 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z24 E5497.71411 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z24 E5509.730683 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z24 E5521.747256 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z24 E5533.76383 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z24 E5545.780403 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z24 E5557.796976 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z24 E5569.813549 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z24 E5581.830123 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z24 E5593.846696 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z24 E5605.863269 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z24 E5617.879843 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z24 E5629.896416 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z24 E5641.912989 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z24 E5653.929563 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z24 E5665.946136 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z24 E5677.962709 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z24 E5689.979283 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z24 E5701.995856 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z24 E5714.012429 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z24 E5726.029002 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z24 E5738.045576 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z24 E5750.062149 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z24 E5762.078722 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z24 E5774.095296 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z24 E5786.111869 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z24 E5798.128442 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z24 E5810.145016 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z24 E5822.161589 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z24 E5834.178162 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z24 E5846.194735 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z24 E5858.211309 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z24 E5870.227882 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z24 E5882.244455 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z24 E5894.261029 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z24 E5906.277602 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z24 E5918.294175 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z24 E5930.310749 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z24 E5942.327322 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z24 E5954.343895 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z24 E5966.360469 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z24 E5978.377042 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z24 E5990.393615 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z24 E6002.410188 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z24 E6014.426762 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z24 E6026.443335 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z24 E6038.459908 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z24 E6050.476482 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z24 E6062.493055 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z24 E6074.509628 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z24 E6086.526202 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z24 E6098.542775 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z24 E6637.318285 F2400 ; clayline kind=carry page=2 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z24 E6649.334858 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z24 E6661.351432 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z24 E6673.368005 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z24 E6685.384578 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z24 E6697.401152 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z24 E6709.417725 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z24 E6721.434298 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z24 E6733.450872 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z24 E6745.467445 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z24 E6757.484018 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z24 E6769.500591 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z24 E6781.517165 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z24 E6793.533738 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z24 E6805.550311 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z24 E6817.566885 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z24 E6829.583458 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z24 E6841.600031 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z24 E6853.616605 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z24 E6865.633178 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z24 E6877.649751 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z24 E6889.666324 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z24 E6901.682898 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z24 E6913.699471 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z24 E6925.716044 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z24 E6937.732618 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z24 E6949.749191 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z24 E6961.765764 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z24 E6973.782338 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z24 E6985.798911 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z24 E6997.815484 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z24 E7009.832058 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z24 E7021.848631 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z24 E7033.865204 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z24 E7045.881777 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z24 E7057.898351 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z24 E7069.914924 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z24 E7081.931497 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z24 E7093.948071 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z24 E7105.964644 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z24 E7117.981217 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z24 E7129.997791 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z24 E7142.014364 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z24 E7154.030937 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z24 E7166.04751 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z24 E7178.064084 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z24 E7190.080657 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z24 E7202.09723 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z24 E7214.113804 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z24 E7226.130377 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z24 E7238.14695 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z24 E7250.163524 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z24 E7262.180097 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z24 E7274.19667 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z24 E7286.213244 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z24 E7298.229817 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z24 E7310.24639 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z24 E7322.262963 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z24 E7334.279537 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z24 E7346.29611 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z24 E7358.312683 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z24 E7370.329257 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z24 E7382.34583 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z24 E7394.362403 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z24 E7406.378977 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.549068 Y203.498795 Z24 E7408.583058 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z24 E7410.542242 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z24 E7411.380163 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z24 E7412.31722 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z24 E7413.786608 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z24 E7414.917639 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z24 E7415.031801 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z24 E7416.011393 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z24 E7416.746087 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z24 E7416.978922 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z24 E7417.292318 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z24 E7417.537216 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z24 E7417.574366 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.482736 Y212.235648 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X240.451968 Y214.284918 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X241.71326 Y216.389256 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X243.174739 Y218.359832 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X244.82233 Y220.17767 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X245.098654 Y220.428114 Z24 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0001
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
