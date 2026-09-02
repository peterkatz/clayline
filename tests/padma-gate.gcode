; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=padma-gate
; prepared_trace_sha256=d52e26c0bf97345e9c7c425fca9c3aff4e4c159765179eddb4474c6d2a841c4f
; body_sha256=bb6949d16869949709fe2c7eb2e82210640d3b88717c13eda8853464f4da453b
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
; stats.motion_count=725
; stats.print_motion_count=724
; stats.travel_motion_count=1
; stats.stroke_count=1
; stats.page_count=1
; stats.print_path_mm=2114.71602
; stats.deposited_path_mm=2114.71602
; stats.travel_path_mm=89.880343
; stats.total_motion_path_mm=2204.596363
; stats.motion_time_seconds=55.114909
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=55.114909
; stats.body_volume_mm3=41522.35196
; stats.wet_weight_g=74.740234
; stats.body_e=17262.98792
; stats.pressure_e_excluded=0
; stats.warning_count=25
; nominal_label=nominal — drape mode: physical bead placement depends on fall
; stats.warning_count.tight_radius=13
; stats.warning_count.under_spaced=12
; parameter.alternate=true
; parameter.flow_modulation=0.0
; parameter.hardware_default_status=calibration pending, provisional reference defaults
; parameter.helical=false
; parameter.layers=1
; parameter.overlap_fraction_provisional=0.2
; parameter.page_gap=30.0
; parameter.page_pause_seconds=disabled
; parameter.page_travel_clearance=50.0
; parameter.provisional_flow_multiplier=1.0
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-01-padma-gate page_name=padma-gate z_mode=drape
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X143.945 Y266.055 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start
G1 X145.321 Y267.219 Z20 E14.712623 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.908 Y268.172 Z20 E29.824099 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.708 Y268.912 Z20 E45.711248 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.718 Y269.442 Z20 E62.68024 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.941 Y269.759 Z20 E81.010757 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.375 Y269.865 Z20 E100.898978 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.97 Y269.865 Z20 E464.939795 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.97 Y272.683 Z20 E487.943876 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.182 Y273.741 Z20 E496.752293 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.605 Y274.588 Z20 E504.480875 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.24 Y275.223 Z20 E511.811696 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.637 Y275.461 Z20 E515.590265 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.589 Y275.779 Z20 E523.783793 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.145 Y275.858 Z20 E528.368155 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.829 Y275.858 Z20 E599.257951 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.887 Y275.646 Z20 E608.066368 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.734 Y275.223 Z20 E615.79495 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.078 Y274.932 Z20 E619.473105 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.607 Y274.191 Z20 E626.905363 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.925 Y273.239 Z20 E635.09889 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.004 Y272.683 Z20 E639.683252 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.03 Y264.608 Z20 E705.601962 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.925 Y263.443 Z20 E715.150714 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.607 Y262.491 Z20 E723.344242 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.369 Y262.094 Z20 E727.122811 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.734 Y261.459 Z20 E734.453632 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.337 Y261.221 Z20 E738.232201 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.385 Y260.903 Z20 E746.425729 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.22 Y260.798 Z20 E755.974481 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.145 Y260.824 Z20 E821.89319 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.087 Y261.036 Z20 E830.701607 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.24 Y261.459 Z20 E838.430189 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.896 Y261.75 Z20 E842.108345 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.367 Y262.491 Z20 E849.540602 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.049 Y263.443 Z20 E857.73413 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.97 Y263.999 Z20 E862.318492 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.97 Y269.865 Z20 E910.204206 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.93056 Y269.865 Z20 E942.535311 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.295 Y270.153 Z20 E946.327148 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.296 Y270.696 Z20 E955.623419 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.365 Y270.999 Z20 E964.693722 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.487 Y271.093 Z20 E973.884993 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.609 Y270.999 Z20 E983.076264 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.678 Y270.696 Z20 E992.146567 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.679 Y270.153 Z20 E1001.442838 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.151 Y269.78 Z20 E1006.353793 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.024 Y268.814 Z20 E1016.982619 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.422 Y268.213 Z20 E1022.866997 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.133 Y266.753 Z20 E1036.123499 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.442 Y265.886 Z20 E1043.637118 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.958 Y263.859 Z20 E1060.711783 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.161 Y262.691 Z20 E1070.389413 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.449 Y260.025 Z20 E1092.279296 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.566 Y256.893 Z20 E1117.864477 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.497 Y253.262 Z20 E1147.510644 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.695 Y250.56 Z20 E1169.626929 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.736 Y247.991 Z20 E1190.601029 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.584 Y243.159 Z20 E1230.065438 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.078 Y237.363 Z20 E1277.559686 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.493 Y233.079 Z20 E1312.855667 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.672 Y228.541 Z20 E1350.50194 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.584 Y223.817 Z20 E1390.074769 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.197 Y218.979 Z20 E1431.159611 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.48 Y214.094 Z20 E1473.428707 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.487 Y211.657 Z20 E1494.91069 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.494 Y214.094 Z20 E1516.392672 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.777 Y218.979 Z20 E1558.661769 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.39 Y223.817 Z20 E1599.74661 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.302 Y228.541 Z20 E1639.31944 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.481 Y233.079 Z20 E1676.965712 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.896 Y237.363 Z20 E1712.261694 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.39 Y243.159 Z20 E1759.755941 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.238 Y247.991 Z20 E1799.220351 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.279 Y250.56 Z20 E1820.19445 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.477 Y253.262 Z20 E1842.310735 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.408 Y256.893 Z20 E1871.956903 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.525 Y260.025 Z20 E1897.542083 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.813 Y262.691 Z20 E1919.431967 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.016 Y263.859 Z20 E1929.109596 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.532 Y265.886 Z20 E1946.184261 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.841 Y266.753 Z20 E1953.697881 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.552 Y268.213 Z20 E1966.954383 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.95 Y268.814 Z20 E1972.838761 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.823 Y269.78 Z20 E1983.467586 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.93056 Y269.865 Z20 E1984.586705 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X259.599 Y269.865 Z20 E2439.022947 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.033 Y269.759 Z20 E2458.911168 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.256 Y269.442 Z20 E2477.241685 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.266 Y268.912 Z20 E2494.210677 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.066 Y268.172 Z20 E2510.097826 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.653 Y267.219 Z20 E2525.209302 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X271.029 Y266.055 Z20 E2539.921925 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.193 Y264.679 Z20 E2554.634548 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.146 Y263.092 Z20 E2569.746024 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.886 Y261.292 Z20 E2585.633173 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.416 Y259.282 Z20 E2602.602165 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.733 Y257.059 Z20 E2620.932683 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.839 Y254.625 Z20 E2640.820903 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.839 Y206.06944 Z20 E3037.192824 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.127 Y205.705 Z20 E3040.984661 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.67 Y204.704 Z20 E3050.280933 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.973 Y203.635 Z20 E3059.351235 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X276.067 Y202.513 Z20 E3068.542506 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.973 Y201.391 Z20 E3077.733778 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.67 Y200.322 Z20 E3086.80408 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.127 Y199.321 Z20 E3096.100351 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.754 Y198.849 Z20 E3101.011307 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.788 Y197.976 Z20 E3111.640132 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.187 Y197.578 Z20 E3117.52451 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X271.727 Y196.867 Z20 E3130.781012 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.86 Y196.558 Z20 E3138.294632 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.833 Y196.042 Z20 E3155.369297 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.665 Y195.839 Z20 E3165.046926 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.999 Y195.551 Z20 E3186.93681 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.961397 Y195.549595 Z20 E3187.243986 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.77219 Y194.015545 Z20 E3199.861739 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.286237 Y191.214929 Z20 E3223.065521 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X263.66345 Y188.441532 Z20 E3246.269302 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.905329 Y185.702034 Z20 E3269.473084 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.0137 Y183.003035 Z20 E3292.676866 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.990711 Y180.351037 Z20 E3315.880647 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X259.838828 Y177.752429 Z20 E3339.084429 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.560824 Y175.213472 Z20 E3362.288211 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.159779 Y172.740282 Z20 E3385.491992 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.639068 Y170.338817 Z20 E3408.695774 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X254.002355 Y168.014862 Z20 E3431.899556 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.253581 Y165.774016 Z20 E3455.103337 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.058458 Y165.547814 Z20 E3457.541961 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.306 Y164.673 Z20 E3464.963696 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.395 Y164.02 Z20 E3470.343592 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.373 Y162.808 Z20 E3480.239099 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.27 Y162.245 Z20 E3484.911297 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.897 Y161.201 Z20 E3493.961355 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.328 Y160.259 Z20 E3502.94512 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.592 Y159.408 Z20 E3512.12978 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.741 Y158.672 Z20 E3521.314441 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.799 Y158.103 Z20 E3530.298206 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.755 Y157.73 Z20 E3539.348263 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.192 Y157.627 Z20 E3544.020462 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.98 Y157.605 Z20 E3553.915969 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.327 Y157.694 Z20 E3559.295864 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.924 Y158.091 Z20 E3571.198616 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.171 Y158.407 Z20 E3577.864886 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.557 Y159.291 Z20 E3592.887184 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.693 Y159.868 Z20 E3601.368439 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.846 Y161.308 Z20 E3620.486885 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.833 Y163.156 Z20 E3642.794078 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.643 Y165.443 Z20 E3668.642731 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.838 Y166.968 Z20 E3687.932322 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X231.225 Y168.523 Z20 E3706.222033 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.355 Y171.609 Z20 E3740.624455 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.235 Y174.14 Z20 E3767.576042 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.912 Y178.595 Z20 E3812.945995 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.694 Y181.973 Z20 E3845.934484 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X218.552 Y185.654 Z20 E3880.700723 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.55 Y189.618 Z20 E3916.952699 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.754 Y193.843 Z20 E3954.429325 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.953 Y196.047 Z20 E3973.572517 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.157 Y195.246 Z20 E3992.715708 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.382 Y193.45 Z20 E4030.192335 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.346 Y191.448 Z20 E4066.44431 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.027 Y189.306 Z20 E4101.210549 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X231.405 Y187.088 Z20 E4134.199039 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.86 Y183.765 Z20 E4179.568991 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.391 Y181.645 Z20 E4206.520579 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.477 Y178.775 Z20 E4240.923 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.032 Y177.162 Z20 E4259.212712 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.557 Y175.357 Z20 E4278.502302 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.844 Y173.167 Z20 E4304.350955 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.692 Y171.154 Z20 E4326.658148 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.132 Y169.307 Z20 E4345.776594 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.709 Y168.443 Z20 E4354.25785 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.593 Y166.829 Z20 E4369.280148 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.909 Y166.076 Z20 E4375.946417 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.058458 Y165.547814 Z20 E4380.427434 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.396962 Y163.621678 Z20 E4401.192592 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.436968 Y161.563032 Z20 E4424.396373 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.378322 Y159.603038 Z20 E4447.600155 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.225984 Y157.746419 Z20 E4470.803937 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.985138 Y155.997645 Z20 E4494.007718 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.661183 Y154.360932 Z20 E4517.2115 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.259718 Y152.840221 Z20 E4540.415282 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.786528 Y151.439176 Z20 E4563.619063 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.247571 Y150.161172 Z20 E4586.822845 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X229.648963 Y149.009289 Z20 E4610.026627 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.996965 Y147.9863 Z20 E4633.230408 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.297966 Y147.094671 Z20 E4656.43419 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X221.558468 Y146.33655 Z20 E4679.637972 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X218.785071 Y145.713763 Z20 E4702.841753 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.984455 Y145.22781 Z20 E4726.045535 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.163369 Y144.879862 Z20 E4749.249317 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.328607 Y144.670758 Z20 E4772.453098 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.487 Y144.601 Z20 E4795.65688 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.645393 Y144.670758 Z20 E4818.860662 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.810631 Y144.879862 Z20 E4842.064443 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.989545 Y145.22781 Z20 E4865.268225 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X196.188929 Y145.713763 Z20 E4888.472007 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X193.415532 Y146.33655 Z20 E4911.675788 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.676034 Y147.094671 Z20 E4934.87957 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.977035 Y147.9863 Z20 E4958.083351 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X185.325037 Y149.009289 Z20 E4981.287133 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.726429 Y150.161172 Z20 E5004.490915 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.187472 Y151.439176 Z20 E5027.694696 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.714282 Y152.840221 Z20 E5050.898478 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.312817 Y154.360932 Z20 E5074.10226 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.988862 Y155.997645 Z20 E5097.306041 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.748016 Y157.746419 Z20 E5120.509823 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.521814 Y157.941542 Z20 E5122.948446 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.647 Y157.694 Z20 E5130.370182 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.994 Y157.605 Z20 E5135.750077 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.782 Y157.627 Z20 E5145.645585 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.219 Y157.73 Z20 E5150.317783 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.175 Y158.103 Z20 E5159.367841 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.233 Y158.672 Z20 E5168.351606 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.382 Y159.408 Z20 E5177.536266 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.646 Y160.259 Z20 E5186.720926 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.077 Y161.201 Z20 E5195.704692 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.704 Y162.245 Z20 E5204.754749 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.601 Y162.808 Z20 E5209.426948 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.579 Y164.02 Z20 E5219.322455 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.668 Y164.673 Z20 E5224.70235 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.065 Y166.076 Z20 E5236.605102 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.381 Y166.829 Z20 E5243.271372 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.265 Y168.443 Z20 E5258.29367 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.842 Y169.307 Z20 E5266.774925 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.282 Y171.154 Z20 E5285.893371 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.13 Y173.167 Z20 E5308.200564 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.417 Y175.357 Z20 E5334.049217 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.942 Y177.162 Z20 E5353.338808 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.497 Y178.775 Z20 E5371.628519 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.583 Y181.645 Z20 E5406.030941 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X179.114 Y183.765 Z20 E5432.982528 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X183.569 Y187.088 Z20 E5478.352481 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.947 Y189.306 Z20 E5511.34097 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.628 Y191.448 Z20 E5546.107209 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.592 Y193.45 Z20 E5582.359185 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.817 Y195.246 Z20 E5619.835811 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.021 Y196.047 Z20 E5638.979003 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.22 Y193.843 Z20 E5658.122194 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.424 Y189.618 Z20 E5695.59882 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X196.422 Y185.654 Z20 E5731.850796 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.28 Y181.973 Z20 E5766.617035 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.062 Y178.595 Z20 E5799.605525 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.739 Y174.14 Z20 E5844.975477 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.619 Y171.609 Z20 E5871.927065 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X183.749 Y168.523 Z20 E5906.329486 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.136 Y166.968 Z20 E5924.619198 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.331 Y165.443 Z20 E5943.908788 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X178.141 Y163.156 Z20 E5969.757441 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.128 Y161.308 Z20 E5992.064634 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.281 Y159.868 Z20 E6011.18308 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.417 Y159.291 Z20 E6019.664335 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.803 Y158.407 Z20 E6034.686633 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.05 Y158.091 Z20 E6041.352903 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.521814 Y157.941542 Z20 E6045.833919 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.595678 Y159.603038 Z20 E6066.599078 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.537032 Y161.563032 Z20 E6089.802859 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.577038 Y163.621678 Z20 E6113.006641 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.720419 Y165.774016 Z20 E6136.210423 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X160.971645 Y168.014862 Z20 E6159.414204 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.334932 Y170.338817 Z20 E6182.617986 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.814221 Y172.740282 Z20 E6205.821767 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.413176 Y175.213472 Z20 E6229.025549 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.135172 Y177.752429 Z20 E6252.229331 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X153.983289 Y180.351037 Z20 E6275.433112 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.9603 Y183.003035 Z20 E6298.636894 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.068671 Y185.702034 Z20 E6321.840676 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X151.31055 Y188.441532 Z20 E6345.044457 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.687763 Y191.214929 Z20 E6368.248239 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.20181 Y194.015545 Z20 E6391.452021 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.853862 Y196.836631 Z20 E6414.655802 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.644758 Y199.671393 Z20 E6437.859584 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.575 Y202.513 Z20 E6461.063366 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.644758 Y205.354607 Z20 E6484.267147 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.853862 Y208.189369 Z20 E6507.470929 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.20181 Y211.010455 Z20 E6530.674711 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.687763 Y213.811071 Z20 E6553.878492 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X151.31055 Y216.584468 Z20 E6577.082274 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.068671 Y219.323966 Z20 E6600.286056 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.9603 Y222.022965 Z20 E6623.489837 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X153.983289 Y224.674963 Z20 E6646.693619 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.135172 Y227.273571 Z20 E6669.897401 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.413176 Y229.812528 Z20 E6693.101182 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X157.814221 Y232.285718 Z20 E6716.304964 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.334932 Y234.687183 Z20 E6739.508746 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X160.971645 Y237.011138 Z20 E6762.712527 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.720419 Y239.251984 Z20 E6785.916309 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.915542 Y239.478186 Z20 E6788.354932 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.668 Y240.353 Z20 E6795.776668 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.579 Y241.006 Z20 E6801.156563 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.601 Y242.218 Z20 E6811.052071 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.704 Y242.781 Z20 E6815.724269 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.077 Y243.825 Z20 E6824.774326 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.646 Y244.767 Z20 E6833.758092 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.382 Y245.618 Z20 E6842.942752 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X165.233 Y246.354 Z20 E6852.127412 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.175 Y246.923 Z20 E6861.111177 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.219 Y247.296 Z20 E6870.161235 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X167.782 Y247.399 Z20 E6874.833433 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.994 Y247.421 Z20 E6884.728941 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X169.647 Y247.332 Z20 E6890.108836 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.05 Y246.935 Z20 E6902.011588 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.803 Y246.619 Z20 E6908.677857 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.417 Y245.735 Z20 E6923.700155 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X174.281 Y245.158 Z20 E6932.181411 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.128 Y243.718 Z20 E6951.299857 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X178.141 Y241.87 Z20 E6973.60705 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.331 Y239.583 Z20 E6999.455703 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.136 Y238.058 Z20 E7018.745293 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X183.749 Y236.503 Z20 E7037.035005 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.619 Y233.417 Z20 E7071.437426 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X188.739 Y230.886 Z20 E7098.389014 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X192.062 Y226.431 Z20 E7143.758966 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.28 Y223.053 Z20 E7176.747456 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X196.422 Y219.372 Z20 E7211.513695 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.424 Y215.408 Z20 E7247.765671 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.22 Y211.183 Z20 E7285.242297 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.021 Y208.979 Z20 E7304.385488 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.817 Y209.78 Z20 E7323.52868 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X194.592 Y211.576 Z20 E7361.005306 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.628 Y213.578 Z20 E7397.257282 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.947 Y215.72 Z20 E7432.023521 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X183.569 Y217.938 Z20 E7465.01201 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X179.114 Y221.261 Z20 E7510.381963 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.583 Y223.381 Z20 E7537.33355 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X173.497 Y226.251 Z20 E7571.735972 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X171.942 Y227.864 Z20 E7590.025683 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.417 Y229.669 Z20 E7609.315274 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.13 Y231.859 Z20 E7635.163927 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.282 Y233.872 Z20 E7657.47112 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.842 Y235.719 Z20 E7676.589566 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.265 Y236.583 Z20 E7685.070821 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.381 Y238.197 Z20 E7700.093119 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X163.065 Y238.95 Z20 E7706.759389 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.915542 Y239.478186 Z20 E7711.240405 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X164.577038 Y241.404322 Z20 E7732.005563 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.537032 Y243.462968 Z20 E7755.209345 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X168.595678 Y245.422962 Z20 E7778.413127 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X170.748016 Y247.279581 Z20 E7801.616908 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.988862 Y249.028355 Z20 E7824.82069 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X175.312817 Y250.665068 Z20 E7848.024472 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X177.714282 Y252.185779 Z20 E7871.228253 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X180.187472 Y253.586824 Z20 E7894.432035 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X182.726429 Y254.864828 Z20 E7917.635817 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X185.325037 Y256.016711 Z20 E7940.839598 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X187.977035 Y257.0397 Z20 E7964.04338 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X190.676034 Y257.931329 Z20 E7987.247162 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X193.415532 Y258.68945 Z20 E8010.450943 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X196.188929 Y259.312237 Z20 E8033.654725 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.989545 Y259.79819 Z20 E8056.858506 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.810631 Y260.146138 Z20 E8080.062288 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.645393 Y260.355242 Z20 E8103.26607 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.487 Y260.425 Z20 E8126.469851 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.328607 Y260.355242 Z20 E8149.673633 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.163369 Y260.146138 Z20 E8172.877415 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.984455 Y259.79819 Z20 E8196.081196 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X218.785071 Y259.312237 Z20 E8219.284978 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X221.558468 Y258.68945 Z20 E8242.48876 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.297966 Y257.931329 Z20 E8265.692541 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.996965 Y257.0397 Z20 E8288.896323 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X229.648963 Y256.016711 Z20 E8312.100105 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.247571 Y254.864828 Z20 E8335.303886 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.786528 Y253.586824 Z20 E8358.507668 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.259718 Y252.185779 Z20 E8381.71145 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X239.661183 Y250.665068 Z20 E8404.915231 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.985138 Y249.028355 Z20 E8428.119013 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.225984 Y247.279581 Z20 E8451.322795 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.452186 Y247.084458 Z20 E8453.761418 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.327 Y247.332 Z20 E8461.183154 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.98 Y247.421 Z20 E8466.563049 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.192 Y247.399 Z20 E8476.458556 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.755 Y247.296 Z20 E8481.130755 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.799 Y246.923 Z20 E8490.180812 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X249.741 Y246.354 Z20 E8499.164577 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.592 Y245.618 Z20 E8508.349238 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.328 Y244.767 Z20 E8517.533898 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.897 Y243.825 Z20 E8526.517663 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.27 Y242.781 Z20 E8535.567721 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.373 Y242.218 Z20 E8540.239919 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.395 Y241.006 Z20 E8550.135426 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.306 Y240.353 Z20 E8555.515322 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.909 Y238.95 Z20 E8567.418074 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X251.593 Y238.197 Z20 E8574.084343 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.709 Y236.583 Z20 E8589.106641 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.132 Y235.719 Z20 E8597.587897 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.692 Y233.872 Z20 E8616.706343 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.844 Y231.859 Z20 E8639.013536 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.557 Y229.669 Z20 E8664.862189 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.032 Y227.864 Z20 E8684.151779 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.477 Y226.251 Z20 E8702.441491 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.391 Y223.381 Z20 E8736.843912 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.86 Y221.261 Z20 E8763.7955 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X231.405 Y217.938 Z20 E8809.165452 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.027 Y215.72 Z20 E8842.153942 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.346 Y213.578 Z20 E8876.920181 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.382 Y211.576 Z20 E8913.172156 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.157 Y209.78 Z20 E8950.648783 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.953 Y208.979 Z20 E8969.791974 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.754 Y211.183 Z20 E8988.935165 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.55 Y215.408 Z20 E9026.411792 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X218.552 Y219.372 Z20 E9062.663768 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X220.694 Y223.053 Z20 E9097.430007 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X222.912 Y226.431 Z20 E9130.418496 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X226.235 Y230.886 Z20 E9175.788449 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.355 Y233.417 Z20 E9202.740036 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X231.225 Y236.503 Z20 E9237.142457 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X232.838 Y238.058 Z20 E9255.432169 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X234.643 Y239.583 Z20 E9274.72176 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X236.833 Y241.87 Z20 E9300.570413 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.846 Y243.718 Z20 E9322.877606 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.693 Y245.158 Z20 E9341.996052 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X241.557 Y245.735 Z20 E9350.477307 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.171 Y246.619 Z20 E9365.499605 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X243.924 Y246.935 Z20 E9372.165875 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X244.452186 Y247.084458 Z20 E9376.646891 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X246.378322 Y245.422962 Z20 E9397.412049 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.436968 Y243.462968 Z20 E9420.615831 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.396962 Y241.404322 Z20 E9443.819612 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.253581 Y239.251984 Z20 E9467.023394 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X254.002355 Y237.011138 Z20 E9490.227176 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.639068 Y234.687183 Z20 E9513.430957 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X257.159779 Y232.285718 Z20 E9536.634739 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.560824 Y229.812528 Z20 E9559.838521 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X259.838828 Y227.273571 Z20 E9583.042302 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.990711 Y224.674963 Z20 E9606.246084 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.0137 Y222.022965 Z20 E9629.449866 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.905329 Y219.323966 Z20 E9652.653647 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X263.66345 Y216.584468 Z20 E9675.857429 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.286237 Y213.811071 Z20 E9699.061211 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.77219 Y211.010455 Z20 E9722.264992 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.120138 Y208.189369 Z20 E9745.468774 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.329242 Y205.354607 Z20 E9768.672556 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.399 Y202.513 Z20 E9791.876337 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.329242 Y199.671393 Z20 E9815.080119 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.120138 Y196.836631 Z20 E9838.283901 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.961397 Y195.549595 Z20 E9848.869929 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X261.867 Y195.434 Z20 E9874.147933 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.236 Y195.503 Z20 E9903.794101 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.534 Y195.305 Z20 E9925.910386 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.965 Y195.264 Z20 E9946.884485 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.133 Y195.416 Z20 E9986.348894 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.337 Y195.922 Z20 E10033.843142 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.053 Y196.507 Z20 E10069.139124 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X233.515 Y197.328 Z20 E10106.785396 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.791 Y198.416 Z20 E10146.358226 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X223.953 Y199.803 Z20 E10187.443067 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.068 Y201.52 Z20 E10229.712163 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.631 Y202.513 Z20 E10251.194146 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.869 Y202.513 Z20 E10257.414554 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.707942 Y200.877753 Z20 E10270.8281 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.230958 Y199.305347 Z20 E10284.241646 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.456378 Y197.85621 Z20 E10297.655191 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.413969 Y196.586031 Z20 E10311.068737 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.14379 Y195.543622 Z20 E10324.482283 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.694653 Y194.769042 Z20 E10337.895828 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.122247 Y194.292058 Z20 E10351.309374 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.487 Y194.131 Z20 E10364.72292 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.851753 Y194.292058 Z20 E10378.136465 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.279347 Y194.769042 Z20 E10391.550011 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.83021 Y195.543622 Z20 E10404.963556 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.560031 Y196.586031 Z20 E10418.377102 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.517622 Y197.85621 Z20 E10431.790648 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.743042 Y199.305347 Z20 E10445.204193 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.266058 Y200.877753 Z20 E10458.617739 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.105 Y202.513 Z20 E10472.031285 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.266058 Y204.148247 Z20 E10485.44483 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.743042 Y205.720653 Z20 E10498.858376 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.517622 Y207.16979 Z20 E10512.271922 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.560031 Y208.439969 Z20 E10525.685467 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.83021 Y209.482378 Z20 E10539.099013 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.279347 Y210.256958 Z20 E10552.512558 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.851753 Y210.733942 Z20 E10565.926104 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.487 Y210.895 Z20 E10579.33965 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.122247 Y210.733942 Z20 E10592.753195 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.694653 Y210.256958 Z20 E10606.166741 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.14379 Y209.482378 Z20 E10619.580287 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.413969 Y208.439969 Z20 E10632.993832 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.456378 Y207.16979 Z20 E10646.407378 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.230958 Y205.720653 Z20 E10659.820924 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.707942 Y204.148247 Z20 E10673.234469 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.869 Y202.513 Z20 E10686.648015 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X216.631 Y202.513 Z20 E10692.868423 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X219.068 Y203.506 Z20 E10714.350406 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X223.953 Y205.223 Z20 E10756.619502 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.791 Y206.61 Z20 E10797.704344 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X233.515 Y207.698 Z20 E10837.277173 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X238.053 Y208.519 Z20 E10874.923445 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.337 Y209.104 Z20 E10910.219427 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X248.133 Y209.61 Z20 E10957.713675 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X252.965 Y209.762 Z20 E10997.178084 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.534 Y209.721 Z20 E11018.152183 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.236 Y209.523 Z20 E11040.268468 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X261.867 Y209.592 Z20 E11069.914636 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.999 Y209.475 Z20 E11095.499816 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.665 Y209.187 Z20 E11117.3897 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.833 Y208.984 Z20 E11127.067329 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X270.86 Y208.468 Z20 E11144.141995 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X271.727 Y208.159 Z20 E11151.655614 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.187 Y207.448 Z20 E11164.912116 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.788 Y207.05 Z20 E11170.796494 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.754 Y206.177 Z20 E11181.425319 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.839 Y206.06944 Z20 E11182.544438 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.839 Y194.977113 Z20 E11273.094047 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.973 Y194.996 Z20 E11320.98001 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.915 Y195.208 Z20 E11329.788426 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.068 Y195.631 Z20 E11337.517008 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.724 Y195.922 Z20 E11341.195164 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.195 Y196.663 Z20 E11348.627421 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.877 Y197.615 Z20 E11356.820949 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.798 Y198.171 Z20 E11361.405311 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.798 Y206.855 Z20 E11432.295107 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.01 Y207.913 Z20 E11441.103524 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.433 Y208.76 Z20 E11448.832106 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.724 Y209.104 Z20 E11452.510261 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.465 Y209.633 Z20 E11459.942519 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.417 Y209.951 Z20 E11468.136046 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.973 Y210.03 Z20 E11472.720409 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.657 Y210.03 Z20 E11543.610205 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.715 Y209.818 Z20 E11552.418621 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.562 Y209.395 Z20 E11560.147203 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.906 Y209.104 Z20 E11563.825359 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.435 Y208.363 Z20 E11571.257616 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.753 Y207.411 Z20 E11579.451144 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.832 Y206.855 Z20 E11584.035506 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.858 Y198.78 Z20 E11649.954215 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.753 Y197.615 Z20 E11659.502968 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.435 Y196.663 Z20 E11667.696495 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X280.197 Y196.266 Z20 E11671.475064 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.562 Y195.631 Z20 E11678.805886 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X279.165 Y195.393 Z20 E11682.584455 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X278.213 Y195.075 Z20 E11690.777982 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.048 Y194.97 Z20 E11700.326735 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.839 Y194.977113 Z20 E11718.359481 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.839 Y150.401 Z20 E12082.246115 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.733 Y147.967 Z20 E12102.134335 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.416 Y145.744 Z20 E12120.464853 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.886 Y143.734 Z20 E12137.433845 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X273.146 Y141.934 Z20 E12153.320994 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.193 Y140.347 Z20 E12168.43247 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X271.029 Y138.971 Z20 E12183.145093 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.653 Y137.807 Z20 E12197.857716 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X268.066 Y136.854 Z20 E12212.969192 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X266.266 Y136.114 Z20 E12228.856341 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X264.256 Y135.584 Z20 E12245.825333 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X262.033 Y135.267 Z20 E12264.15585 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X259.599 Y135.161 Z20 E12284.044071 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.04344 Y135.161 Z20 E12680.415992 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.679 Y134.873 Z20 E12684.207829 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X209.678 Y134.33 Z20 E12693.5041 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.609 Y134.027 Z20 E12702.574403 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.487 Y133.933 Z20 E12711.765674 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.365 Y134.027 Z20 E12720.956945 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X205.296 Y134.33 Z20 E12730.027248 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.295 Y134.873 Z20 E12739.323519 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.823 Y135.246 Z20 E12744.234474 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.95 Y136.212 Z20 E12754.8633 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.552 Y136.813 Z20 E12760.747678 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.841 Y138.273 Z20 E12774.00418 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.532 Y139.14 Z20 E12781.517799 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.016 Y141.167 Z20 E12798.592464 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.813 Y142.335 Z20 E12808.270094 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.525 Y145.001 Z20 E12830.159978 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.408 Y148.133 Z20 E12855.745158 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.477 Y151.764 Z20 E12885.391326 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.279 Y154.466 Z20 E12907.507611 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.238 Y157.035 Z20 E12928.48171 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.39 Y161.867 Z20 E12967.946119 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.896 Y167.663 Z20 E13015.440367 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.481 Y171.947 Z20 E13050.736349 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.302 Y176.485 Z20 E13088.382621 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.39 Y181.209 Z20 E13127.95545 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X204.777 Y186.047 Z20 E13169.040292 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X206.494 Y190.932 Z20 E13211.309388 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X207.487 Y193.369 Z20 E13232.791371 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X208.48 Y190.932 Z20 E13254.273354 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X210.197 Y186.047 Z20 E13296.54245 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.584 Y181.209 Z20 E13337.627291 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.672 Y176.485 Z20 E13377.200121 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.493 Y171.947 Z20 E13414.846393 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.078 Y167.663 Z20 E13450.142375 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.584 Y161.867 Z20 E13497.636623 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.736 Y157.035 Z20 E13537.101032 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.695 Y154.466 Z20 E13558.075131 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.497 Y151.764 Z20 E13580.191416 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.566 Y148.133 Z20 E13609.837584 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.449 Y145.001 Z20 E13635.422764 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.161 Y142.335 Z20 E13657.312648 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.958 Y141.167 Z20 E13666.990277 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.442 Y139.14 Z20 E13684.064942 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.133 Y138.273 Z20 E13691.578562 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.422 Y136.813 Z20 E13704.835064 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.024 Y136.212 Z20 E13710.719442 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.151 Y135.246 Z20 E13721.348267 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.04344 Y135.161 Z20 E13722.467386 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.97 Y135.161 Z20 E13812.862812 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.97 Y141.027 Z20 E13860.748526 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.182 Y142.085 Z20 E13869.556943 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.605 Y142.932 Z20 E13877.285525 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.24 Y143.567 Z20 E13884.616346 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.637 Y143.805 Z20 E13888.394915 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.589 Y144.123 Z20 E13896.588443 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.145 Y144.202 Z20 E13901.172805 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.829 Y144.202 Z20 E13972.062601 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.887 Y143.99 Z20 E13980.871018 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.734 Y143.567 Z20 E13988.5996 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.078 Y143.276 Z20 E13992.277755 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.607 Y142.535 Z20 E13999.710013 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.925 Y141.583 Z20 E14007.90354 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.004 Y141.027 Z20 E14012.487902 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X215.03 Y132.952 Z20 E14078.406611 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.925 Y131.787 Z20 E14087.955364 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.607 Y130.835 Z20 E14096.148892 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X214.369 Y130.438 Z20 E14099.927461 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.734 Y129.803 Z20 E14107.258282 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X213.337 Y129.565 Z20 E14111.036851 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X212.385 Y129.247 Z20 E14119.230379 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X211.22 Y129.142 Z20 E14128.779131 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X203.145 Y129.168 Z20 E14194.69784 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X202.087 Y129.38 Z20 E14203.506257 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X201.24 Y129.803 Z20 E14211.234839 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.605 Y130.438 Z20 E14218.56566 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.367 Y130.835 Z20 E14222.344229 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X200.049 Y131.787 Z20 E14230.537757 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.97 Y132.343 Z20 E14235.122119 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X199.97 Y135.161 Z20 E14258.126201 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X155.375 Y135.161 Z20 E14622.167017 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X152.941 Y135.267 Z20 E14642.055238 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X150.718 Y135.584 Z20 E14660.385755 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.708 Y136.114 Z20 E14677.354747 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.908 Y136.854 Z20 E14693.241896 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X145.321 Y137.807 Z20 E14708.353372 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X143.945 Y138.971 Z20 E14723.065995 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.781 Y140.347 Z20 E14737.778618 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.828 Y141.934 Z20 E14752.890095 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.088 Y143.734 Z20 E14768.777244 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.558 Y145.744 Z20 E14785.746235 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.241 Y147.967 Z20 E14804.076753 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.135 Y150.401 Z20 E14823.964974 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.135 Y194.986927 Z20 E15187.931721 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.317 Y194.996 Z20 E15210.935922 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.259 Y195.208 Z20 E15219.744339 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.412 Y195.631 Z20 E15227.47292 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.777 Y196.266 Z20 E15234.803742 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.539 Y196.663 Z20 E15238.582311 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.221 Y197.615 Z20 E15246.775838 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.142 Y198.171 Z20 E15251.360201 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.142 Y206.855 Z20 E15322.249997 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.354 Y207.913 Z20 E15331.058413 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X134.777 Y208.76 Z20 E15338.786995 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.068 Y209.104 Z20 E15342.465151 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X135.809 Y209.633 Z20 E15349.897408 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X136.761 Y209.951 Z20 E15358.090936 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X137.317 Y210.03 Z20 E15362.675298 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.001 Y210.03 Z20 E15433.565094 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.059 Y209.818 Z20 E15442.373511 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.906 Y209.395 Z20 E15450.102093 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.25 Y209.104 Z20 E15453.780248 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.779 Y208.363 Z20 E15461.212506 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.097 Y207.411 Z20 E15469.406033 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.176 Y206.855 Z20 E15473.990396 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.202 Y198.78 Z20 E15539.909105 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.097 Y197.615 Z20 E15549.457857 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.779 Y196.663 Z20 E15557.651385 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X148.541 Y196.266 Z20 E15561.429954 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.906 Y195.631 Z20 E15568.760775 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.509 Y195.393 Z20 E15572.539344 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.557 Y195.075 Z20 E15580.732872 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X145.392 Y194.97 Z20 E15590.281624 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.135 Y194.986927 Z20 E15633.196133 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.135 Y198.95656 Z20 E15665.601306 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.847 Y199.321 Z20 E15669.393143 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.304 Y200.322 Z20 E15678.689414 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.001 Y201.391 Z20 E15687.759717 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X138.907 Y202.513 Z20 E15696.950988 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.001 Y203.635 Z20 E15706.142259 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.304 Y204.704 Z20 E15715.212562 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X139.847 Y205.705 Z20 E15724.508833 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.22 Y206.177 Z20 E15729.419789 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.186 Y207.05 Z20 E15740.048614 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.787 Y207.448 Z20 E15745.932992 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X143.247 Y208.159 Z20 E15759.189494 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.114 Y208.468 Z20 E15766.703113 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.141 Y208.984 Z20 E15783.777779 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.309 Y209.187 Z20 E15793.455408 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.975 Y209.475 Z20 E15815.345292 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X153.107 Y209.592 Z20 E15840.930472 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.738 Y209.523 Z20 E15870.57664 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.44 Y209.721 Z20 E15892.692925 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.009 Y209.762 Z20 E15913.667024 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.841 Y209.61 Z20 E15953.131433 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.637 Y209.104 Z20 E16000.625681 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.921 Y208.519 Z20 E16035.921663 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X181.459 Y207.698 Z20 E16073.567935 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.183 Y206.61 Z20 E16113.140764 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X191.021 Y205.223 Z20 E16154.225606 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.906 Y203.506 Z20 E16196.494702 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X198.343 Y202.513 Z20 E16217.976685 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X195.906 Y201.52 Z20 E16239.458668 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X191.021 Y199.803 Z20 E16281.727764 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X186.183 Y198.416 Z20 E16322.812606 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X181.459 Y197.328 Z20 E16362.385435 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X176.921 Y196.507 Z20 E16400.031707 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X172.637 Y195.922 Z20 E16435.327689 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X166.841 Y195.416 Z20 E16482.821937 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X162.009 Y195.264 Z20 E16522.286346 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X159.44 Y195.305 Z20 E16543.260445 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X156.738 Y195.503 Z20 E16565.37673 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X153.107 Y195.434 Z20 E16595.022898 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X149.975 Y195.551 Z20 E16620.608078 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X147.309 Y195.839 Z20 E16642.497962 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X146.141 Y196.042 Z20 E16652.175591 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X144.114 Y196.558 Z20 E16669.250257 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X143.247 Y196.867 Z20 E16676.763876 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.787 Y197.578 Z20 E16690.020378 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.186 Y197.976 Z20 E16695.904756 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.22 Y198.849 Z20 E16706.533581 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.135 Y198.95656 Z20 E16707.6527 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.135 Y254.625 Z20 E17162.088942 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.241 Y257.059 Z20 E17181.977163 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X140.558 Y259.282 Z20 E17200.30768 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.088 Y261.292 Z20 E17217.276672 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X141.828 Y263.092 Z20 E17233.163821 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X142.781 Y264.679 Z20 E17248.275297 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X143.945 Y266.055 Z20 E17262.98792 F2400 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
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
