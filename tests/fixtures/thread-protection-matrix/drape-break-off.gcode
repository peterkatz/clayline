; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=drape-job
; prepared_trace_sha256=a0fbbea91a62ee23bd9525cc566c42148a48053c24ce500925b4a55796e4fd1c
; body_sha256=c10eb228991329143957471f1dff3f6c7c8687a1c2c95b8a538629b2bb1ac7cf
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
; stats.motion_count=451
; stats.print_motion_count=444
; stats.travel_motion_count=7
; stats.stroke_count=6
; stats.page_count=3
; stats.print_path_mm=1332.099347
; stats.deposited_path_mm=1301.539952
; stats.travel_path_mm=337.91478
; stats.total_motion_path_mm=1670.014127
; stats.motion_time_seconds=49.097292
; stats.pause_time_seconds=4
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=53.097292
; stats.body_volume_mm3=15774.209909
; stats.wet_weight_g=28.393578
; stats.body_e=6558.154398
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
G1 X237.549068 Y203.498795 Z20 E2177.060159 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z20 E2179.019342 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z20 E2179.857264 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z20 E2180.79432 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z20 E2182.263708 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z20 E2183.394739 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z20 E2183.508901 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z20 E2184.488493 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z20 E2185.223187 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z20 E2185.456023 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z20 E2185.769418 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z20 E2186.014316 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z20 E2186.051466 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.482736 Y212.235648 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X240.451968 Y214.284918 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X241.71326 Y216.389256 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X243.174739 Y218.359832 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X244.82233 Y220.17767 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
G1 X245.098654 Y220.428114 Z20 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=1
G0 X245.098654 Y220.428114 Z26 F2400 ; clayline kind=travel_lift page=1 layer=0 stroke=stroke-0000 note=inter-page clearance above completed material
G0 X127.5 Y202.5 Z26 F2400 ; clayline kind=travel_xy page=1 layer=0 stroke=stroke-0000 note=inter-page XY within common stack footprint
G4 S2
G0 X127.5 Y202.5 Z22 F2400 ; clayline kind=travel_approach page=1 layer=0 stroke=stroke-0000 note=inter-page approach
G1 E2284.01065 F2400 ; clayline kind=thread_launch page=1 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=1 layer=0 text=layer 0 page_id=page-02-drape page_name=drape z_mode=drape
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z22 E2296.027223 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z22 E2308.043796 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z22 E2320.06037 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z22 E2332.076943 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z22 E2344.093516 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z22 E2356.110089 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z22 E2368.126663 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z22 E2380.143236 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z22 E2392.159809 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z22 E2404.176383 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z22 E2416.192956 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z22 E2428.209529 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z22 E2440.226103 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z22 E2452.242676 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z22 E2464.259249 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z22 E2476.275822 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z22 E2488.292396 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z22 E2500.308969 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z22 E2512.325542 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z22 E2524.342116 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z22 E2536.358689 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z22 E2548.375262 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z22 E2560.391836 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z22 E2572.408409 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z22 E2584.424982 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z22 E2596.441556 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z22 E2608.458129 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z22 E2620.474702 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z22 E2632.491275 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z22 E2644.507849 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z22 E2656.524422 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z22 E2668.540995 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z22 E2680.557569 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z22 E2692.574142 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z22 E2704.590715 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z22 E2716.607289 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z22 E2728.623862 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z22 E2740.640435 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z22 E2752.657009 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z22 E2764.673582 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z22 E2776.690155 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z22 E2788.706728 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z22 E2800.723302 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z22 E2812.739875 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z22 E2824.756448 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z22 E2836.773022 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z22 E2848.789595 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z22 E2860.806168 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z22 E2872.822742 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z22 E2884.839315 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z22 E2896.855888 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z22 E2908.872461 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z22 E2920.889035 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z22 E2932.905608 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z22 E2944.922181 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z22 E2956.938755 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z22 E2968.955328 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z22 E2980.971901 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z22 E2992.988475 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z22 E3005.005048 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z22 E3017.021621 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z22 E3029.038195 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z22 E3041.054768 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z22 E3053.071341 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z22 E3591.846851 F2400 ; clayline kind=carry page=1 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=1 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z22 E3603.863425 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z22 E3615.879998 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z22 E3627.896571 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z22 E3639.913145 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z22 E3651.929718 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z22 E3663.946291 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z22 E3675.962864 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z22 E3687.979438 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z22 E3699.996011 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z22 E3712.012584 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z22 E3724.029158 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z22 E3736.045731 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z22 E3748.062304 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z22 E3760.078878 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z22 E3772.095451 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z22 E3784.112024 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z22 E3796.128598 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z22 E3808.145171 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z22 E3820.161744 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z22 E3832.178317 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z22 E3844.194891 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z22 E3856.211464 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z22 E3868.228037 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z22 E3880.244611 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z22 E3892.261184 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z22 E3904.277757 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z22 E3916.294331 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z22 E3928.310904 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z22 E3940.327477 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z22 E3952.34405 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z22 E3964.360624 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z22 E3976.377197 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z22 E3988.39377 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z22 E4000.410344 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z22 E4012.426917 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z22 E4024.44349 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z22 E4036.460064 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z22 E4048.476637 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z22 E4060.49321 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z22 E4072.509784 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z22 E4084.526357 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z22 E4096.54293 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z22 E4108.559503 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z22 E4120.576077 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z22 E4132.59265 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z22 E4144.609223 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z22 E4156.625797 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z22 E4168.64237 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z22 E4180.658943 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z22 E4192.675517 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z22 E4204.69209 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z22 E4216.708663 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z22 E4228.725236 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z22 E4240.74181 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z22 E4252.758383 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z22 E4264.774956 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z22 E4276.79153 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z22 E4288.808103 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z22 E4300.824676 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z22 E4312.84125 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z22 E4324.857823 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z22 E4336.874396 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z22 E4348.89097 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z22 E4360.907543 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001
G1 X237.549068 Y203.498795 Z22 E4363.111624 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z22 E4365.070808 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z22 E4365.90873 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z22 E4366.845786 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z22 E4368.315174 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z22 E4369.446205 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z22 E4369.560367 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z22 E4370.539959 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z22 E4371.274653 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z22 E4371.507489 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z22 E4371.820884 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z22 E4372.065782 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z22 E4372.102932 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.482736 Y212.235648 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X240.451968 Y214.284918 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X241.71326 Y216.389256 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X243.174739 Y218.359832 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X244.82233 Y220.17767 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
G1 X245.098654 Y220.428114 Z22 F2400 ; clayline kind=print page=1 layer=0 stroke=stroke-0001 note=thread landing
; CLAYLINE_STROKE_END page=1 layer=0 id=stroke-0001
; CLAYLINE_PAGE index=2
G0 X245.098654 Y220.428114 Z28 F2400 ; clayline kind=travel_lift page=2 layer=0 stroke=stroke-0000 note=inter-page clearance above completed material
G0 X127.5 Y202.5 Z28 F2400 ; clayline kind=travel_xy page=2 layer=0 stroke=stroke-0000 note=inter-page XY within common stack footprint
G4 S2
G0 X127.5 Y202.5 Z24 F2400 ; clayline kind=travel_approach page=2 layer=0 stroke=stroke-0000 note=inter-page approach
G1 E4470.062116 F2400 ; clayline kind=thread_launch page=2 layer=0 stroke=stroke-0000 note=thread launch
; CLAYLINE_MARKER page=2 layer=0 text=layer 0 page_id=page-03-drape page_name=drape z_mode=drape
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0000
G1 X127.620382 Y204.950429 Z24 E4482.078689 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y207.377258 Z24 E4494.095262 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y209.757117 Z24 E4506.111835 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y212.067086 Z24 E4518.128409 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y214.284918 Z24 E4530.144982 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y216.389256 Z24 E4542.161555 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y218.359832 Z24 E4554.178129 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y220.17767 Z24 E4566.194702 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y221.825261 Z24 E4578.211275 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y223.28674 Z24 E4590.227849 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y224.548032 Z24 E4602.244422 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y225.596988 Z24 E4614.260995 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y226.423508 Z24 E4626.277569 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y227.019632 Z24 E4638.294142 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y227.379618 Z24 E4650.310715 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y227.5 Z24 E4662.327288 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y227.379618 Z24 E4674.343862 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y227.019632 Z24 E4686.360435 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y226.423508 Z24 E4698.377008 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y225.596988 Z24 E4710.393582 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y224.548032 Z24 E4722.410155 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y223.28674 Z24 E4734.426728 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y221.825261 Z24 E4746.443302 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y220.17767 Z24 E4758.459875 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y218.359832 Z24 E4770.476448 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y216.389256 Z24 E4782.493021 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y214.284918 Z24 E4794.509595 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y212.067086 Z24 E4806.526168 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y209.757117 Z24 E4818.542741 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y207.377258 Z24 E4830.559315 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y204.950429 Z24 E4842.575888 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.5 Y202.5 Z24 E4854.592461 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.379618 Y200.049571 Z24 E4866.609035 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X177.019632 Y197.622742 Z24 E4878.625608 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X176.423508 Y195.242883 Z24 E4890.642181 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X175.596988 Y192.932914 Z24 E4902.658755 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X174.548032 Y190.715082 Z24 E4914.675328 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X173.28674 Y188.610744 Z24 E4926.691901 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X171.825261 Y186.640168 Z24 E4938.708474 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X170.17767 Y184.82233 Z24 E4950.725048 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X168.359832 Y183.174739 Z24 E4962.741621 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X166.389256 Y181.71326 Z24 E4974.758194 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X164.284918 Y180.451968 Z24 E4986.774768 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X162.067086 Y179.403012 Z24 E4998.791341 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X159.757117 Y178.576492 Z24 E5010.807914 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X157.377258 Y177.980368 Z24 E5022.824488 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X154.950429 Y177.620382 Z24 E5034.841061 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X152.5 Y177.5 Z24 E5046.857634 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X150.049571 Y177.620382 Z24 E5058.874207 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X147.622742 Y177.980368 Z24 E5070.890781 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X145.242883 Y178.576492 Z24 E5082.907354 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X142.932914 Y179.403012 Z24 E5094.923927 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X140.715082 Y180.451968 Z24 E5106.940501 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X138.610744 Y181.71326 Z24 E5118.957074 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X136.640168 Y183.174739 Z24 E5130.973647 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X134.82233 Y184.82233 Z24 E5142.990221 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X133.174739 Y186.640168 Z24 E5155.006794 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X131.71326 Y188.610744 Z24 E5167.023367 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X130.451968 Y190.715082 Z24 E5179.039941 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X129.403012 Y192.932914 Z24 E5191.056514 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X128.576492 Y195.242883 Z24 E5203.073087 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.980368 Y197.622742 Z24 E5215.08966 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.620382 Y200.049571 Z24 E5227.106234 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
G1 X127.5 Y202.5 Z24 E5239.122807 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=2 layer=0 id=stroke-0000
G1 X237.5 Y202.5 Z24 E5777.898317 F2400 ; clayline kind=carry page=2 layer=0 stroke=stroke-0001 note=thread carry across gap
; CLAYLINE_STROKE_BEGIN page=2 layer=0 id=stroke-0001
G1 X237.620382 Y204.950429 Z24 E5789.914891 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y207.377258 Z24 E5801.931464 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y209.757117 Z24 E5813.948037 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y212.067086 Z24 E5825.96461 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y214.284918 Z24 E5837.981184 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y216.389256 Z24 E5849.997757 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y218.359832 Z24 E5862.01433 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y220.17767 Z24 E5874.030904 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y221.825261 Z24 E5886.047477 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y223.28674 Z24 E5898.06405 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y224.548032 Z24 E5910.080624 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y225.596988 Z24 E5922.097197 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y226.423508 Z24 E5934.11377 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y227.019632 Z24 E5946.130344 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y227.379618 Z24 E5958.146917 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y227.5 Z24 E5970.16349 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y227.379618 Z24 E5982.180063 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y227.019632 Z24 E5994.196637 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y226.423508 Z24 E6006.21321 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y225.596988 Z24 E6018.229783 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y224.548032 Z24 E6030.246357 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y223.28674 Z24 E6042.26293 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y221.825261 Z24 E6054.279503 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y220.17767 Z24 E6066.296077 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y218.359832 Z24 E6078.31265 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y216.389256 Z24 E6090.329223 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y214.284918 Z24 E6102.345796 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y212.067086 Z24 E6114.36237 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y209.757117 Z24 E6126.378943 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y207.377258 Z24 E6138.395516 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y204.950429 Z24 E6150.41209 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.5 Y202.5 Z24 E6162.428663 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.379618 Y200.049571 Z24 E6174.445236 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X287.019632 Y197.622742 Z24 E6186.46181 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X286.423508 Y195.242883 Z24 E6198.478383 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X285.596988 Y192.932914 Z24 E6210.494956 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X284.548032 Y190.715082 Z24 E6222.51153 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X283.28674 Y188.610744 Z24 E6234.528103 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X281.825261 Y186.640168 Z24 E6246.544676 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X280.17767 Y184.82233 Z24 E6258.561249 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X278.359832 Y183.174739 Z24 E6270.577823 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X276.389256 Y181.71326 Z24 E6282.594396 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X274.284918 Y180.451968 Z24 E6294.610969 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X272.067086 Y179.403012 Z24 E6306.627543 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X269.757117 Y178.576492 Z24 E6318.644116 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X267.377258 Y177.980368 Z24 E6330.660689 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X264.950429 Y177.620382 Z24 E6342.677263 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X262.5 Y177.5 Z24 E6354.693836 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X260.049571 Y177.620382 Z24 E6366.710409 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X257.622742 Y177.980368 Z24 E6378.726982 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X255.242883 Y178.576492 Z24 E6390.743556 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X252.932914 Y179.403012 Z24 E6402.760129 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X250.715082 Y180.451968 Z24 E6414.776702 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X248.610744 Y181.71326 Z24 E6426.793276 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X246.640168 Y183.174739 Z24 E6438.809849 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X244.82233 Y184.82233 Z24 E6450.826422 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X243.174739 Y186.640168 Z24 E6462.842996 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X241.71326 Y188.610744 Z24 E6474.859569 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X240.451968 Y190.715082 Z24 E6486.876142 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X239.403012 Y192.932914 Z24 E6498.892716 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X238.576492 Y195.242883 Z24 E6510.909289 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.980368 Y197.622742 Z24 E6522.925862 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.620382 Y200.049571 Z24 E6534.942435 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.5 Y202.5 Z24 E6546.959009 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001
G1 X237.549068 Y203.498795 Z24 E6549.16309 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.598135 Y204.497591 Z24 E6551.122274 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.620382 Y204.950429 Z24 E6551.960196 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.700587 Y205.491128 Z24 E6552.897252 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.847318 Y206.480305 Z24 E6554.36664 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X237.980368 Y207.377258 Z24 E6555.497671 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.003022 Y207.467697 Z24 E6555.611833 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.246002 Y208.437728 Z24 E6556.591425 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.488982 Y209.407759 Z24 E6557.326119 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.576492 Y209.757117 Z24 E6557.558955 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X238.79205 Y210.359563 Z24 E6557.87235 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.12894 Y211.301107 Z24 E6558.117248 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
G1 X239.403012 Y212.067086 Z24 E6558.154398 F2400 ; clayline kind=print page=2 layer=0 stroke=stroke-0001 note=thread landing
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
