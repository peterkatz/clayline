; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=pages-job-page-02-rosette
; prepared_trace_sha256=bfc1844210debf22cdb776eedf9b647c6d7eb1c9ef7cb54db42eb2d04611cb96
; body_sha256=6391d0a373589f86d51e7b320abe5c64560ccc5583be3db0883ea87d70c6cbf9
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
; stats.motion_count=3214
; stats.print_motion_count=3109
; stats.travel_motion_count=105
; stats.stroke_count=36
; stats.page_count=1
; stats.print_path_mm=4586.450349
; stats.deposited_path_mm=4406.450349
; stats.travel_path_mm=1097.511304
; stats.total_motion_path_mm=5683.961653
; stats.motion_time_seconds=161.074128
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=161.074128
; stats.body_volume_mm3=43416.513932
; stats.wet_weight_g=78.149725
; stats.body_e=18050.488958
; stats.pressure_e_excluded=0
; stats.warning_count=59
; nominal_label=calibrated centerline
; stats.warning_count.tight_radius=4
; stats.warning_count.under_spaced=55
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
; parameter.split_source_page=2
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
; CLAYLINE_MARKER page=0 layer=0 text=layer 0 page_id=page-1-rosette-1 page_name=rosette z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0000
G0 X231.683462 Y360.031538 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0000 note=stroke start XY at safe Z
G0 X231.683462 Y360.031538 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0000 note=stroke start vertical approach
G1 X232.794889 Y361.038876 Z2 E0.342995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X233.622731 Y361.789189 Z2 E1.044245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X233.930143 Y362.017181 Z2 E1.371981 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X235.134954 Y362.91073 Z2 E3.086956 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X235.724942 Y363.348295 Z2 E4.17698 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X236.381499 Y363.74182 Z2 E5.487922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X237.668092 Y364.512974 Z2 E8.574879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X237.969849 Y364.69384 Z2 E9.398205 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X239.007801 Y365.184755 Z2 E12.347825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X240.335833 Y365.812867 Z2 E16.707921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X240.364946 Y365.823284 Z2 E16.806762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X241.777262 Y366.328619 Z2 E21.951689 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X242.800108 Y366.694599 Z2 E26.106126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X243.201362 Y366.795108 Z2 E27.782607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X244.656409 Y367.159578 Z2 E34.299514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=prime ramp
G1 X245.338941 Y367.330543 Z2 E37.517351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.927883 Y367.714577 Z2 E49.486828 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.542 Y367.843 Z2 E61.456306 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.156117 Y367.714577 Z2 E73.425783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.745059 Y367.330543 Z2 E85.395261 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.283892 Y366.694599 Z2 E97.364738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.748167 Y365.812867 Z2 E109.334215 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X263.114151 Y364.69384 Z2 E121.303693 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.359058 Y363.348295 Z2 E133.27317 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.461269 Y361.789189 Z2 E145.242648 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.400538 Y360.031538 Z2 E157.212125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X271.158189 Y358.092269 Z2 E169.181603 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.717295 Y355.990058 Z2 E181.15108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.06284 Y353.745151 Z2 E193.120558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.181867 Y351.379167 Z2 E205.090035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X276.063599 Y348.914892 Z2 E217.059513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X276.699543 Y346.376059 Z2 E229.02899 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.083577 Y343.787117 Z2 E240.998468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.212 Y341.173 Z2 E252.967945 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X277.083577 Y338.558883 Z2 E264.937423 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X276.699543 Y335.969941 Z2 E276.9069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X276.063599 Y333.431108 Z2 E288.876378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X275.181867 Y330.966833 Z2 E300.845855 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X274.06284 Y328.600849 Z2 E312.815333 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X272.717295 Y326.355942 Z2 E324.78481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X271.158189 Y324.253731 Z2 E336.754288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X269.400538 Y322.314462 Z2 E348.723765 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X267.461269 Y320.556811 Z2 E360.693242 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X265.359058 Y318.997705 Z2 E372.66272 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X263.114151 Y317.65216 Z2 E384.632197 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X260.748167 Y316.533133 Z2 E396.601675 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X258.283892 Y315.651401 Z2 E408.571152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X255.745059 Y315.015457 Z2 E420.54063 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X253.156117 Y314.631423 Z2 E432.510107 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X250.542 Y314.503 Z2 E444.479585 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X247.927883 Y314.631423 Z2 E456.449062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X245.338941 Y315.015457 Z2 E468.41854 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X242.800108 Y315.651401 Z2 E480.388017 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X240.335833 Y316.533133 Z2 E492.357495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X237.969849 Y317.65216 Z2 E504.326972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X235.724942 Y318.997705 Z2 E516.29645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X233.622731 Y320.556811 Z2 E528.265927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X231.683462 Y322.314462 Z2 E540.235405 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X229.925811 Y324.253731 Z2 E552.204882 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.366705 Y326.355942 Z2 E564.17436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X227.02116 Y328.600849 Z2 E576.143837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X225.902133 Y330.966833 Z2 E588.113315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X225.020401 Y333.431108 Z2 E600.082792 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.384457 Y335.969941 Z2 E612.05227 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.000423 Y338.558883 Z2 E624.021747 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X223.872 Y341.173 Z2 E635.991224 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.000423 Y343.787117 Z2 E647.960702 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X224.384457 Y346.376059 Z2 E659.930179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X225.020401 Y348.914892 Z2 E671.899657 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X225.902133 Y351.379167 Z2 E683.869134 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X227.02116 Y353.745151 Z2 E695.838612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.366705 Y355.990058 Z2 E707.808089 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X228.50642 Y356.178442 Z2 E708.880701 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000
G1 X229.925811 Y358.092269 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
G1 X231.683462 Y360.031538 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0000 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0000
G0 X231.683462 Y360.031538 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0001 note=intra-page lift
G0 X243.537431 Y348.177569 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0001 note=intra-page XY
G0 X243.537431 Y348.177569 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0001
G1 X244.648858 Y349.184907 Z2 E709.223697 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X244.867216 Y349.382815 Z2 E709.37171 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X245.835322 Y350.100812 Z2 E710.252682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X246.308732 Y350.451916 Z2 E710.844735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X247.089781 Y350.920059 Z2 E711.967658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X247.848096 Y351.374576 Z2 E713.299776 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X248.404865 Y351.637908 Z2 E714.368624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X249.470485 Y352.141909 Z2 E716.736834 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X249.772912 Y352.250119 Z2 E717.45558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X251.160274 Y352.746525 Z2 E721.155908 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X251.185983 Y352.752965 Z2 E721.228527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X252.64103 Y353.117435 Z2 E725.687463 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X252.901188 Y353.182601 Z2 E726.557 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X254.11966 Y353.363344 Z2 E730.832391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X254.676463 Y353.445938 Z2 E732.940107 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X255.612439 Y353.49192 Z2 E736.663308 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X256.469 Y353.534 Z2 E740.305231 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X257.110632 Y353.502479 Z2 E743.180216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=prime ramp
G1 X258.261537 Y353.445938 Z2 E748.449962 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.036812 Y353.182601 Z2 E756.657604 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X261.777726 Y352.746525 Z2 E764.865246 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X263.467515 Y352.141909 Z2 E773.072888 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X265.089904 Y351.374576 Z2 E781.280529 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X266.629268 Y350.451916 Z2 E789.488171 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X268.070784 Y349.382815 Z2 E797.695813 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X269.400569 Y348.177569 Z2 E805.903454 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X270.605815 Y346.847784 Z2 E814.111096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X271.674916 Y345.406268 Z2 E822.318738 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X272.597576 Y343.866904 Z2 E830.526379 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X273.364909 Y342.244515 Z2 E838.734021 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X273.969525 Y340.554726 Z2 E846.941663 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.405601 Y338.813812 Z2 E855.149305 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.668938 Y337.038537 Z2 E863.356946 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.757 Y335.246 Z2 E871.564588 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.668938 Y333.453463 Z2 E879.77223 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X274.405601 Y331.678188 Z2 E887.979871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X273.969525 Y329.937274 Z2 E896.187513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X273.503236 Y328.634085 Z2 E902.517364 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X273.364909 Y328.247485 Z2.205301 E904.616798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2 matz1=2.205301 note=collision lift
G1 X272.597576 Y326.625096 Z3.10265 E913.79322 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.205301 matz1=3.10265 note=collision lift
G1 X271.674916 Y325.085732 Z4 E922.969643 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=3.10265 matz1=4 note=collision lift
G1 X270.605815 Y323.644216 Z4 E931.177284 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=4 matz1=4 note=collision lift
G1 X269.400569 Y322.314431 Z3.10265 E940.353707 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=4 matz1=3.10265 note=collision lift
G1 X268.070784 Y321.109185 Z4 E949.530129 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=3.10265 matz1=4 note=collision lift
G1 X266.629268 Y320.040084 Z4 E957.737771 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=4 matz1=4 note=collision lift
G1 X265.089904 Y319.117424 Z3.10265 E966.914193 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=4 matz1=3.10265 note=collision lift
G1 X263.467515 Y318.350091 Z2.205301 E976.090616 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=3.10265 matz1=2.205301 note=collision lift
G1 X263.080915 Y318.211764 Z2 E978.19005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 matz0=2.205301 matz1=2 note=collision lift
G1 X261.777726 Y317.745475 Z2 E984.5199 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X260.036812 Y317.309399 Z2 E992.727542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X258.261537 Y317.046062 Z2 E1000.935184 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X256.469 Y316.958 Z2 E1009.142826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X254.676463 Y317.046062 Z2 E1017.350467 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X252.901188 Y317.309399 Z2 E1025.558109 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X251.160274 Y317.745475 Z2 E1033.765751 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X249.470485 Y318.350091 Z2 E1041.973392 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X247.848096 Y319.117424 Z2 E1050.181034 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X246.308732 Y320.040084 Z2 E1058.388676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X244.867216 Y321.109185 Z2 E1066.596317 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X243.537431 Y322.314431 Z2 E1074.803959 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X242.332185 Y323.644216 Z2 E1083.011601 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X241.263084 Y325.085732 Z2 E1091.219243 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.340424 Y326.625096 Z2 E1099.426884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.573091 Y328.247485 Z2 E1107.634526 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.968475 Y329.937274 Z2 E1115.842168 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.532399 Y331.678188 Z2 E1124.049809 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.269062 Y333.453463 Z2 E1132.257451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.181 Y335.246 Z2 E1140.465093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.269062 Y337.038537 Z2 E1148.672734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.532399 Y338.813812 Z2 E1156.880376 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X238.968475 Y340.554726 Z2 E1165.088018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X239.573091 Y342.244515 Z2 E1173.29566 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.340424 Y343.866904 Z2 E1181.503301 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X240.53789 Y344.196355 Z2 E1183.259883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001
G1 X241.263084 Y345.406268 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
G1 X242.332185 Y346.847784 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
G1 X243.537431 Y348.177569 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0001
G0 X243.537431 Y348.177569 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0002 note=intra-page lift
G0 X248.263984 Y315.534088 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0002 note=intra-page XY
G0 X248.263984 Y315.534088 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0002
G1 X249.762177 Y315.60769 Z2 E1183.602879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X250.542 Y315.646 Z2 E1184.05287 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X251.26037 Y315.610709 Z2 E1184.631864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X252.758563 Y315.537107 Z2 E1186.34684 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X252.820016 Y315.534088 Z2 E1186.431831 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X254.24292 Y315.32302 Z2 E1188.747806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X255.076094 Y315.199431 Z2 E1190.396766 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X255.714093 Y315.03962 Z2 E1191.834762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X257.169139 Y314.67515 Z2 E1195.607709 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X257.288506 Y314.64525 Z2 E1195.947674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X258.584961 Y314.181371 Z2 E1200.066645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X259.435946 Y313.876884 Z2 E1203.084556 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X259.974888 Y313.621984 Z2 E1205.211573 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X261.330872 Y312.980651 Z2 E1211.04249 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X261.497732 Y312.901732 Z2 E1211.807412 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X262.626003 Y312.225472 Z2 E1217.559398 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=prime ramp
G1 X263.454008 Y311.729185 Z2 E1221.974182 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X265.285934 Y310.370536 Z2 E1232.404727 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X266.975869 Y308.838869 Z2 E1242.835271 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X268.507536 Y307.148934 Z2 E1253.265816 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X269.866185 Y305.317008 Z2 E1263.69636 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X271.038732 Y303.360732 Z2 E1274.126905 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X272.013884 Y301.298946 Z2 E1284.55745 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X272.78225 Y299.151506 Z2 E1294.987994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X273.336431 Y296.939094 Z2 E1305.418539 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X273.671088 Y294.683016 Z2 E1315.849084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X273.783 Y292.405 Z2 E1326.279628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X273.671088 Y290.126984 Z2 E1336.710173 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X273.336431 Y287.870906 Z2 E1347.140718 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X272.78225 Y285.658494 Z2 E1357.571262 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X272.013884 Y283.511054 Z2 E1368.001807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X271.038732 Y281.449268 Z2 E1378.432352 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X269.866185 Y279.492992 Z2 E1388.862896 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X268.507536 Y277.661066 Z2 E1399.293441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X266.975869 Y275.971131 Z2 E1409.723986 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X265.285934 Y274.439464 Z2 E1420.15453 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X263.454008 Y273.080815 Z2 E1430.585075 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X261.497732 Y271.908268 Z2 E1441.01562 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X259.435946 Y270.933116 Z2 E1451.446164 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X257.288506 Y270.16475 Z2 E1461.876709 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X255.076094 Y269.610569 Z2 E1472.307254 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X252.820016 Y269.275912 Z2 E1482.737798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X250.542 Y269.164 Z2 E1493.168343 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X248.263984 Y269.275912 Z2 E1503.598888 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X246.007906 Y269.610569 Z2 E1514.029432 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X243.795494 Y270.16475 Z2 E1524.459977 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X241.648054 Y270.933116 Z2 E1534.890522 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X239.586268 Y271.908268 Z2 E1545.321066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X237.629992 Y273.080815 Z2 E1555.751611 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X235.798066 Y274.439464 Z2 E1566.182156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X234.108131 Y275.971131 Z2 E1576.6127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X232.576464 Y277.661066 Z2 E1587.043245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X231.217815 Y279.492992 Z2 E1597.47379 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X230.045268 Y281.449268 Z2 E1607.904334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X229.070116 Y283.511054 Z2 E1618.334879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X228.30175 Y285.658494 Z2 E1628.765424 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X227.747569 Y287.870906 Z2 E1639.195968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X227.412912 Y290.126984 Z2 E1649.626513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X227.301 Y292.405 Z2 E1660.057058 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X227.412912 Y294.683016 Z2 E1670.487602 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X227.747569 Y296.939094 Z2 E1680.918147 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X228.30175 Y299.151506 Z2 E1691.348692 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X229.070116 Y301.298946 Z2 E1701.779236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X230.045268 Y303.360732 Z2 E1712.209781 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X231.217815 Y305.317008 Z2 E1722.640325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X232.576464 Y307.148934 Z2 E1733.07087 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X234.108131 Y308.838869 Z2 E1743.501415 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X235.798066 Y310.370536 Z2 E1753.931959 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X237.629992 Y311.729185 Z2 E1764.362504 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X239.586268 Y312.901732 Z2 E1774.793049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X241.648054 Y313.876884 Z2 E1785.223593 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X243.382652 Y314.497533 Z2 E1793.648885 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002
G1 X243.795494 Y314.64525 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X246.007906 Y315.199431 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
G1 X248.263984 Y315.534088 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0002
G0 X248.263984 Y315.534088 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0003 note=intra-page lift
G0 X265.401 Y316.789 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0003 note=intra-page XY
G0 X265.401 Y316.789 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0003 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0003
G1 X265.452335 Y317.310215 Z3.405596 E1793.99188 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2 matz1=2.90429 note=collision lift
G1 X265.50367 Y317.831429 Z4.811192 E1795.020865 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2.90429 matz1=3.808581 note=collision lift
G1 X265.514537 Y317.94176 Z5.108727 E1795.326654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=3.808581 matz1=4 note=collision lift
G1 X265.519477 Y317.991918 Z5.198415 E1795.432325 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.519572 Y317.992877 Z5.197933 E1795.433449 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.524249 Y318.040369 Z5.261745 E1795.517539 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.524417 Y318.042077 Z5.266197 E1795.522635 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.534046 Y318.13984 Z5.370139 E1795.678626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.534298 Y318.142394 Z5.376511 E1795.686275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.553915 Y318.341576 Z5.538675 E1795.983508 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.554058 Y318.343028 Z5.541984 E1795.987825 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.583799 Y318.64499 Z5.729682 E1796.433319 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.58402 Y318.647235 Z5.734194 E1796.439895 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.641562 Y318.836925 Z5.832224 E1796.735841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.740043 Y319.161574 Z6 E1797.27694 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.74457 Y319.176498 Z6 E1797.300173 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X266.065604 Y320.234805 Z6 E1799.136807 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X266.126047 Y320.43406 Z6 E1799.524315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X266.734988 Y321.573308 Z6 E1802.223763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X266.824823 Y321.741377 Z6 E1802.665069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X267.006252 Y322.080806 Z5.807563 E1803.702242 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X267.505084 Y322.688635 Z5.414406 E1805.99671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X268.190808 Y323.524192 Z4.873949 E1809.535418 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X268.392353 Y323.689596 Z5.004313 E1810.455647 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X269.429455 Y324.540724 Z5.675134 E1815.600574 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X269.634194 Y324.708748 Z5.807563 E1816.697332 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X269.973623 Y324.890177 Z6 E1818.338719 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X270.655856 Y325.254838 Z6 E1821.431491 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X271.28094 Y325.588953 Z6 E1824.42535 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X272.038095 Y325.818633 Z6 E1827.948399 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X272.538502 Y325.97043 Z6 E1830.339871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X272.553426 Y325.974957 Z6 E1830.411191 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X273.067765 Y326.13098 Z5.739056 E1833.143617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X274.926 Y326.314 Z4.805443 E1842.690876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X276.784235 Y326.13098 Z3.871829 E1852.238136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=3.871829 note=collision lift
G1 X278.57106 Y325.588953 Z2.938216 E1861.785395 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=3.871829 matz1=2.938216 note=collision lift
G1 X280.217806 Y324.708748 Z2.004603 E1871.332654 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2.938216 matz1=2.004603 note=collision lift
G1 X280.224923 Y324.702908 Z2 E1871.379724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2.004603 matz1=2 note=collision lift
G1 X281.661192 Y323.524192 Z2 E1879.876952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X282.845748 Y322.080806 Z2 E1888.41628 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X283.725953 Y320.43406 Z2 E1896.955609 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X284.26798 Y318.647235 Z2 E1905.494937 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X284.451 Y316.789 Z2 E1914.034266 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X284.26798 Y314.930765 Z2 E1922.573594 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X283.725953 Y313.14394 Z2 E1931.112922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X282.845748 Y311.497194 Z2 E1939.652251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X281.661192 Y310.053808 Z2 E1948.191579 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X280.217806 Y308.869252 Z2 E1956.730907 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X278.57106 Y307.989047 Z2 E1965.270236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X276.784235 Y307.44702 Z2 E1973.809564 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X274.926 Y307.264 Z2 E1982.348893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X273.067765 Y307.44702 Z2 E1990.888221 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X271.28094 Y307.989047 Z2 E1999.427549 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X269.634194 Y308.869252 Z2 E2007.966878 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X268.673489 Y309.657682 Z2 E2013.650579 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003
G1 X268.190808 Y310.053808 Z2.312209 E2016.843267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2 matz1=2.312209 note=collision lift
G1 X267.006252 Y311.497194 Z3.245822 E2026.390526 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=2.312209 matz1=3.245822 note=collision lift
G1 X266.473789 Y312.493362 Z3.810594 E2032.165962 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=3.245822 matz1=3.702048 note=collision lift
G1 X266.126047 Y313.14394 Z4.179435 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=3.702048 matz1=4 note=collision lift
G1 X265.58402 Y314.930765 Z5.113048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.410147 Y316.696126 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
G1 X265.401 Y316.789 Z5.953338 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0003 matz0=4 matz1=4 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0003
G0 X265.401 Y316.789 Z9.953338 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0004 note=intra-page lift
G0 X276.325793 Y308.686622 Z9.953338 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0004 note=intra-page XY
G0 X276.325793 Y308.686622 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0004 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0004
G1 X277.219342 Y309.891433 Z2 E2032.508957 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X277.515743 Y310.291084 Z2 E2032.77425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X278.188935 Y311.033836 Z2 E2033.537942 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X279.196273 Y312.145263 Z2 E2035.252918 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X279.373831 Y312.341169 Z2 E2035.626323 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X280.289353 Y313.170949 Z2 E2037.653884 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X280.510196 Y313.371109 Z2 E2038.212657 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 note=prime ramp
G1 X281.306758 Y314.093071 Z2.537527 E2040.74084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2 matz1=2.537527 note=collision lift
G1 X281.423916 Y314.199257 Z2.616586 E2041.149839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2.537527 matz1=2.616586 note=collision lift
G1 X282.37453 Y314.90428 Z3.208347 E2044.513787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2.616586 matz1=3.208347 note=collision lift
G1 X283.452146 Y315.703495 Z3.879168 E2048.972724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.208347 matz1=3.879168 note=collision lift
G1 X283.646253 Y315.847454 Z4 E2049.848806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.879168 matz1=4 note=collision lift
G1 X284.701097 Y316.479703 Z4 E2054.117651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=4 note=collision lift
G1 X285.671034 Y317.061061 Z4 E2058.449824 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=4 note=collision lift
G1 X285.954259 Y317.23082 Z3.834898 E2059.948568 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=3.834898 note=collision lift
G1 X286.01944 Y317.269888 Z3.796902 E2060.299369 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.834898 matz1=3.796902 note=collision lift
G1 X287.163573 Y317.811022 Z3.164078 E2066.465476 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.796902 matz1=3.164078 note=collision lift
G1 X288.520623 Y318.45286 Z2.413488 E2074.141113 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.164078 matz1=2.413488 note=collision lift
G1 X289.299257 Y318.731459 Z2 E2078.369495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2.413488 matz1=2 note=collision lift
G1 X291.125714 Y319.384976 Z2 E2087.240963 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X293.809623 Y320.05726 Z2 E2099.894411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X296.546505 Y320.463238 Z2 E2112.547858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X299.31 Y320.599 Z2 E2125.201306 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X302.073495 Y320.463238 Z2 E2137.854753 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X304.810377 Y320.05726 Z2 E2150.508201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X307.494286 Y319.384976 Z2 E2163.161649 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X310.099377 Y318.45286 Z2 E2175.815096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X312.60056 Y317.269888 Z2 E2188.468544 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X314.973747 Y315.847454 Z2 E2201.121992 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X317.196084 Y314.199257 Z2 E2213.775439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X319.246169 Y312.341169 Z2 E2226.428887 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X321.104257 Y310.291084 Z2 E2239.082334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X322.752454 Y308.068747 Z2 E2251.735782 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X324.174888 Y305.69556 Z2 E2264.38923 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X325.35786 Y303.194377 Z2 E2277.042677 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X326.289976 Y300.589286 Z2 E2289.696125 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X326.96226 Y297.905377 Z2 E2302.349572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X327.368238 Y295.168495 Z2 E2315.00302 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X327.504 Y292.405 Z2 E2327.656468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X327.368238 Y289.641505 Z2 E2340.309915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X326.96226 Y286.904623 Z2 E2352.963363 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X326.289976 Y284.220714 Z2 E2365.616811 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X325.35786 Y281.615623 Z2 E2378.270258 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X324.174888 Y279.11444 Z2 E2390.923706 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X322.752454 Y276.741253 Z2 E2403.577153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X321.104257 Y274.518916 Z2 E2416.230601 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X319.246169 Y272.468831 Z2 E2428.884049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X317.196084 Y270.610743 Z2 E2441.537496 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X314.973747 Y268.962546 Z2 E2454.190944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X312.60056 Y267.540112 Z2 E2466.844392 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X310.099377 Y266.35714 Z2 E2479.497839 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X307.494286 Y265.425024 Z2 E2492.151287 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X304.810377 Y264.75274 Z2 E2504.804734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X302.073495 Y264.346762 Z2 E2517.458182 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X299.31 Y264.211 Z2 E2530.11163 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X296.546505 Y264.346762 Z2 E2542.765077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X293.809623 Y264.75274 Z2 E2555.418525 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X291.125714 Y265.425024 Z2 E2568.071972 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X288.520623 Y266.35714 Z2 E2580.72542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X286.01944 Y267.540112 Z2 E2593.378868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X283.646253 Y268.962546 Z2 E2606.032315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X281.423916 Y270.610743 Z2 E2618.685763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X279.373831 Y272.468831 Z2 E2631.339211 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X277.515743 Y274.518916 Z2 E2643.992658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X275.867546 Y276.741253 Z2 E2656.646106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X274.445112 Y279.11444 Z2 E2669.299553 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X273.789389 Y280.500849 Z2 E2676.313374 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X273.26214 Y281.615623 Z2.616586 E2682.618669 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2 matz1=2.616586 note=collision lift
G1 X272.330024 Y284.220714 Z4 E2696.765653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2.616586 matz1=4 note=collision lift
G1 X271.782073 Y286.408257 Z4 E2707.078954 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=4 note=collision lift
G1 X271.65774 Y286.904623 Z3.744149 E2709.695318 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=3.744149 note=collision lift
G1 X271.251762 Y289.641505 Z2.360735 E2723.842302 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.744149 matz1=2.360735 note=collision lift
G1 X271.216361 Y290.362107 Z2 E2727.531233 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2.360735 matz1=2 note=collision lift
G1 X271.116 Y292.405 Z2 E2736.885201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X271.216361 Y294.447893 Z2 E2746.239168 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004
G1 X271.251762 Y295.168495 Z2.360735 E2749.928099 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2 matz1=2.360735 note=collision lift
G1 X271.65774 Y297.905377 Z3.744149 E2764.075083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2.360735 matz1=3.744149 note=collision lift
G1 X271.782073 Y298.401743 Z4 E2766.691447 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.744149 matz1=4 note=collision lift
G1 X272.330024 Y300.589286 Z4 E2777.004748 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=4 note=collision lift
G1 X273.26214 Y303.194377 Z2.616586 E2791.151732 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=2.616586 note=collision lift
G1 X273.348976 Y303.377975 Z2.515037 E2792.190188 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2.616586 matz1=2.515037 note=collision lift
G1 X273.938345 Y304.62409 Z3.204268 E2799.238361 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=2.515037 matz1=3.204268 note=collision lift
G1 X274.445112 Y305.69556 Z3.796902 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.204268 matz1=3.796902 note=collision lift
G1 X274.653939 Y306.043966 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=3.796902 matz1=4 note=collision lift
G1 X275.867546 Y308.068747 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=4 note=collision lift
G1 X276.325793 Y308.686622 Z3.615371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0004 matz0=4 matz1=3.615371 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0004
G0 X276.325793 Y308.686622 Z7.615371 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0005 note=intra-page lift
G0 X286.197707 Y321.997357 Z7.615371 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0005 note=intra-page XY
G0 X286.197707 Y321.997357 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0005 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0005
G1 X284.992895 Y322.890906 Z2 E2799.581356 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X284.566066 Y323.207464 Z2 E2799.867431 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X283.848385 Y323.857932 Z2 E2800.610341 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X282.876131 Y324.739131 Z2 E2802.072996 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X282.749992 Y324.878304 Z2 E2802.325317 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X281.742654 Y325.989731 Z2 E2804.726283 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X281.344464 Y326.429066 Z2 E2805.864535 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X280.804125 Y327.157628 Z2 E2807.813239 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X279.985815 Y328.260992 Z2 E2811.242048 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X279.920882 Y328.369326 Z2 E2811.586186 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X279.149728 Y329.655919 Z2 E2816.045123 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X278.813268 Y330.217268 Z2 E2818.205535 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X278.451753 Y330.981627 Z2 E2821.19005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X277.838116 Y332.279054 Z2 E2826.754995 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X277.816294 Y332.340043 Z2 E2827.020967 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X277.310959 Y333.752359 Z2 E2833.537875 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=prime ramp
G1 X277.06975 Y334.426494 Z2 E2836.812282 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X276.515569 Y336.638906 Z2 E2847.242826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X276.180912 Y338.894984 Z2 E2857.673371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X276.069 Y341.173 Z2 E2868.103915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X276.180912 Y343.451016 Z2 E2878.53446 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X276.515569 Y345.707094 Z2 E2888.965005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X277.06975 Y347.919506 Z2 E2899.395549 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X277.838116 Y350.066946 Z2 E2909.826094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X278.813268 Y352.128732 Z2 E2920.256639 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X279.985815 Y354.085008 Z2 E2930.687183 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X281.344464 Y355.916934 Z2 E2941.117728 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X282.876131 Y357.606869 Z2 E2951.548273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X284.566066 Y359.138536 Z2 E2961.978817 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X286.397992 Y360.497185 Z2 E2972.409362 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X288.354268 Y361.669732 Z2 E2982.839907 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X290.416054 Y362.644884 Z2 E2993.270451 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X292.563494 Y363.41325 Z2 E3003.700996 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X294.775906 Y363.967431 Z2 E3014.131541 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X297.031984 Y364.302088 Z2 E3024.562085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X299.31 Y364.414 Z2 E3034.99263 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X301.588016 Y364.302088 Z2 E3045.423175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X303.844094 Y363.967431 Z2 E3055.853719 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X306.056506 Y363.41325 Z2 E3066.284264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X308.203946 Y362.644884 Z2 E3076.714809 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X310.265732 Y361.669732 Z2 E3087.145353 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X312.222008 Y360.497185 Z2 E3097.575898 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X314.053934 Y359.138536 Z2 E3108.006443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X315.743869 Y357.606869 Z2 E3118.436987 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X317.275536 Y355.916934 Z2 E3128.867532 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X318.634185 Y354.085008 Z2 E3139.298077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X319.806732 Y352.128732 Z2 E3149.728621 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X320.781884 Y350.066946 Z2 E3160.159166 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X321.55025 Y347.919506 Z2 E3170.589711 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X322.104431 Y345.707094 Z2 E3181.020255 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X322.439088 Y343.451016 Z2 E3191.4508 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X322.551 Y341.173 Z2 E3201.881345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X322.439088 Y338.894984 Z2 E3212.311889 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X322.104431 Y336.638906 Z2 E3222.742434 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X321.55025 Y334.426494 Z2 E3233.172979 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X320.781884 Y332.279054 Z2 E3243.603523 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X319.806732 Y330.217268 Z2 E3254.034068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X318.634185 Y328.260992 Z2 E3264.464613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X317.275536 Y326.429066 Z2 E3274.895157 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X315.743869 Y324.739131 Z2 E3285.325702 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X314.053934 Y323.207464 Z2 E3295.756247 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X312.222008 Y321.848815 Z2 E3306.186791 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X311.74037 Y321.560132 Z2 E3308.754806 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X310.265732 Y320.676268 Z2.859618 E3317.545382 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=2 matz1=2.859618 note=collision lift
G1 X308.203946 Y319.701116 Z4 E3329.207085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=2.859618 matz1=4 note=collision lift
G1 X306.056506 Y318.93275 Z4 E3339.63763 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=4 matz1=4 note=collision lift
G1 X303.844094 Y318.378569 Z2.859618 E3351.299333 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=4 matz1=2.859618 note=collision lift
G1 X302.143466 Y318.126305 Z2 E3360.089908 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=2.859618 matz1=2 note=collision lift
G1 X301.588016 Y318.043912 Z2 E3362.657924 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X299.31 Y317.932 Z2 E3373.088468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X297.031984 Y318.043912 Z2 E3383.519013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X296.476534 Y318.126305 Z2 E3386.087028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005
G1 X294.775906 Y318.378569 Z2.859618 E3394.877603 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=2 matz1=2.859618 note=collision lift
G1 X292.563494 Y318.93275 Z4 E3406.539307 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=2.859618 matz1=4 note=collision lift
G1 X290.416054 Y319.701116 Z4 E3416.969851 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=4 matz1=4 note=collision lift
G1 X290.187217 Y319.809348 Z3.873429 E3418.26418 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=4 matz1=3.873429 note=collision lift
G1 X288.354268 Y320.676268 Z2.859618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=3.873429 matz1=2.859618 note=collision lift
G1 X286.87963 Y321.560132 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 matz0=2.859618 matz1=2 note=collision lift
G1 X286.397992 Y321.848815 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
G1 X286.197707 Y321.997357 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0005 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0005
G0 X286.197707 Y321.997357 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0006 note=intra-page lift
G0 X294.001274 Y299.999525 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0006 note=intra-page XY
G0 X294.001274 Y299.999525 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0006 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0006
G1 X295.456321 Y300.363995 Z2 E3418.607175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X295.742188 Y300.435601 Z2 E3418.755188 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X296.934443 Y300.612456 Z2 E3419.63616 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X297.517463 Y300.698938 Z2 E3420.228213 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X298.426967 Y300.743619 Z2 E3421.351136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X299.31 Y300.787 Z2 E3422.683254 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X299.92516 Y300.756779 Z2 E3423.752102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X301.102537 Y300.698938 Z2 E3426.120312 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X301.420264 Y300.651808 Z2 E3426.839058 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X302.877812 Y300.435601 Z2 E3430.539387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X302.903521 Y300.429161 Z2 E3430.612005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X304.358568 Y300.064691 Z2 E3435.070942 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X304.618726 Y299.999525 Z2 E3435.940478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X305.778524 Y299.584542 Z2 E3440.215869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X306.308515 Y299.394909 Z2 E3442.323586 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X307.155648 Y298.994245 Z2 E3446.046786 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X307.930904 Y298.627576 Z2 E3449.68871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X308.481913 Y298.297313 Z2 E3452.563694 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=prime ramp
G1 X309.470268 Y297.704916 Z2 E3457.833441 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X310.911784 Y296.635815 Z2 E3466.041083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X312.241569 Y295.430569 Z2 E3474.248724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X313.446815 Y294.100784 Z2 E3482.456366 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X314.515916 Y292.659268 Z2 E3490.664008 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X315.438576 Y291.119904 Z2 E3498.871649 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X316.205909 Y289.497515 Z2 E3507.079291 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X316.810525 Y287.807726 Z2 E3515.286933 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X317.246601 Y286.066812 Z2 E3523.494575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X317.509938 Y284.291537 Z2 E3531.702216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X317.598 Y282.499 Z2 E3539.909858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X317.509938 Y280.706463 Z2 E3548.1175 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X317.246601 Y278.931188 Z2 E3556.325141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X316.810525 Y277.190274 Z2 E3564.532783 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X316.205909 Y275.500485 Z2 E3572.740425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X315.438576 Y273.878096 Z2 E3580.948066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X314.515916 Y272.338732 Z2 E3589.155708 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X313.446815 Y270.897216 Z2 E3597.36335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X312.241569 Y269.567431 Z2 E3605.570992 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X310.911784 Y268.362185 Z2 E3613.778633 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X309.470268 Y267.293084 Z2 E3621.986275 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X307.930904 Y266.370424 Z2 E3630.193917 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X306.679694 Y265.778646 Z2 E3636.523767 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X306.308515 Y265.603091 Z2.205301 E3638.623201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=2 matz1=2.205301 note=collision lift
G1 X304.618726 Y264.998475 Z3.10265 E3647.799624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=2.205301 matz1=3.10265 note=collision lift
G1 X302.877812 Y264.562399 Z4 E3656.976046 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=3.10265 matz1=4 note=collision lift
G1 X301.102537 Y264.299062 Z4 E3665.183688 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=4 matz1=4 note=collision lift
G1 X299.31 Y264.211 Z4 E3673.39133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=4 matz1=4 note=collision lift
G1 X297.517463 Y264.299062 Z3.10265 E3682.567752 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=4 matz1=3.10265 note=collision lift
G1 X295.742188 Y264.562399 Z2.205301 E3691.744174 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=3.10265 matz1=2.205301 note=collision lift
G1 X295.343892 Y264.662167 Z2 E3693.843608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 matz0=2.205301 matz1=2 note=collision lift
G1 X294.001274 Y264.998475 Z2 E3700.173459 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X292.311485 Y265.603091 Z2 E3708.381101 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X290.689096 Y266.370424 Z2 E3716.588743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X289.149732 Y267.293084 Z2 E3724.796384 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X287.708216 Y268.362185 Z2 E3733.004026 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X286.378431 Y269.567431 Z2 E3741.211668 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X285.173185 Y270.897216 Z2 E3749.419309 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X284.104084 Y272.338732 Z2 E3757.626951 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X283.181424 Y273.878096 Z2 E3765.834593 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X282.414091 Y275.500485 Z2 E3774.042235 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X281.809475 Y277.190274 Z2 E3782.249876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X281.373399 Y278.931188 Z2 E3790.457518 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X281.110062 Y280.706463 Z2 E3798.66516 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X281.022 Y282.499 Z2 E3806.872801 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X281.110062 Y284.291537 Z2 E3815.080443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X281.373399 Y286.066812 Z2 E3823.288085 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X281.809475 Y287.807726 Z2 E3831.495726 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X282.414091 Y289.497515 Z2 E3839.703368 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X283.181424 Y291.119904 Z2 E3847.91101 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X284.104084 Y292.659268 Z2 E3856.118652 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X285.173185 Y294.100784 Z2 E3864.326293 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X286.378431 Y295.430569 Z2 E3872.533935 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X287.708216 Y296.635815 Z2 E3880.741577 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X289.149732 Y297.704916 Z2 E3888.949218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X289.479183 Y297.902382 Z2 E3890.705801 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006
G1 X290.689096 Y298.627576 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X292.311485 Y299.394909 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
G1 X294.001274 Y299.999525 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0006 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0006
G0 X294.001274 Y299.999525 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0007 note=intra-page lift
G0 X315.715953 Y311.606263 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0007 note=intra-page XY
G0 X315.715953 Y311.606263 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0007 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0007
G1 X315.097406 Y312.763484 Z2.726801 E3891.048796 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2 matz1=2.726801 note=collision lift
G1 X314.894047 Y313.14394 Z2.965749 E3891.311401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.726801 matz1=2.965749 note=collision lift
G1 X314.638375 Y313.986778 Z3.453601 E3892.077781 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.965749 matz1=3.453601 note=collision lift
G1 X314.35202 Y314.930765 Z4 E3893.303072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.453601 matz1=4 note=collision lift
G1 X314.315526 Y315.301292 Z4 E3893.792757 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=4 matz1=4 note=collision lift
G1 X314.169 Y316.789 Z4 E3896.184408 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=4 matz1=4 note=collision lift
G1 X314.169447 Y316.793534 Z3.997722 E3896.193723 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=4 matz1=3.997722 note=collision lift
G1 X314.30095 Y318.128715 Z3.326901 E3899.280679 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.997722 matz1=3.326901 note=collision lift
G1 X314.35202 Y318.647235 Z3.066387 E3900.664439 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.326901 matz1=3.066387 note=collision lift
G1 X314.590231 Y319.432511 Z2.656081 E3903.053626 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.066387 matz1=2.656081 note=collision lift
G1 X314.894047 Y320.43406 Z2.132773 E3906.473208 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.656081 matz1=2.132773 note=collision lift
G1 X315.019225 Y320.668251 Z2 E3907.40722 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.132773 matz1=2 note=collision lift
G1 X315.034762 Y320.697318 Z2 E3907.512563 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X315.741857 Y322.0202 Z2 E3912.65749 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X315.774252 Y322.080806 Z2 E3912.909635 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X316.682245 Y323.1872 Z2 E3918.488407 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X316.958808 Y323.524192 Z2 E3920.311715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X317.781331 Y324.19922 Z2 E3925.005315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 note=prime ramp
G1 X318.402194 Y324.708748 Z2 E3928.678448 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X320.04894 Y325.588953 Z2 E3937.217776 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X321.835765 Y326.13098 Z2 E3945.757104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X323.694 Y326.314 Z2 E3954.296433 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X325.552235 Y326.13098 Z2 E3962.835761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X327.33906 Y325.588953 Z2 E3971.375089 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X328.985806 Y324.708748 Z2 E3979.914418 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X330.429192 Y323.524192 Z2 E3988.453746 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X331.613748 Y322.080806 Z2 E3996.993074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X332.493953 Y320.43406 Z2 E4005.532403 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X333.03598 Y318.647235 Z2 E4014.071731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X333.219 Y316.789 Z2 E4022.61106 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X333.03598 Y314.930765 Z2 E4031.150388 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X332.493953 Y313.14394 Z2 E4039.689716 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X331.613748 Y311.497194 Z2 E4048.229045 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X330.429192 Y310.053808 Z2 E4056.768373 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X328.985806 Y308.869252 Z2 E4065.307701 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X327.573251 Y308.114225 Z2 E4072.632612 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007
G1 X327.33906 Y307.989047 Z2.132773 E4073.990372 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2 matz1=2.132773 note=collision lift
G1 X325.552235 Y307.44702 Z3.066387 E4083.537632 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.132773 matz1=3.066387 note=collision lift
G1 X323.694 Y307.264 Z4 E4093.084891 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.066387 matz1=4 note=collision lift
G1 X321.835765 Y307.44702 Z4 E4101.624219 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=4 matz1=4 note=collision lift
G1 X320.04894 Y307.989047 Z3.066387 E4111.171479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=4 matz1=3.066387 note=collision lift
G1 X319.636446 Y308.20953 Z2.832526 E4113.562976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.066387 matz1=2.832526 note=collision lift
G1 X319.035262 Y308.53087 Z2.832526 E4116.680463 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.832526 matz1=2.832526 note=collision lift
G1 X318.402194 Y308.869252 Z2.832526 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.832526 matz1=2.832526 note=collision lift
G1 X318.196923 Y309.037713 Z2.832526 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.832526 matz1=2.832526 note=collision lift
G1 X316.958808 Y310.053808 Z3.633365 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=2.832526 matz1=3.633365 note=collision lift
G1 X316.490146 Y310.624874 Z4.002743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.633365 matz1=4 note=collision lift
G1 X315.774252 Y311.497194 Z3.438507 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=4 matz1=3.438507 note=collision lift
G1 X315.715953 Y311.606263 Z3.376671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0007 matz0=3.438507 matz1=3.376671 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0007
G0 X315.715953 Y311.606263 Z7.376671 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0008 note=intra-page lift
G0 X328.081201 Y304.194819 Z7.376671 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0008 note=intra-page XY
G0 X328.081201 Y304.194819 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0008 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0008
G1 X328.753815 Y305.317008 Z2 E4116.941401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X328.867995 Y305.470961 Z2 E4117.023458 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X329.761544 Y306.675773 Z2 E4118.052443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X330.112464 Y307.148934 Z2 E4118.644159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X330.724194 Y307.823874 Z2 E4119.767419 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X331.644131 Y308.838869 Z2 E4121.93289 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X331.740563 Y308.92627 Z2 E4122.168385 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X332.85199 Y309.933608 Z2 E4125.255341 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X333.334066 Y310.370536 Z2 E4126.807595 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X334.016296 Y310.876513 Z2 E4129.028288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X335.165992 Y311.729185 Z2 E4133.268273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X335.224849 Y311.764462 Z2 E4133.487225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X336.511442 Y312.535617 Z2 E4138.632152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X337.122268 Y312.901732 Z2 E4141.314926 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X337.834481 Y313.238584 Z2 E4144.463069 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X339.184054 Y313.876884 Z2 E4150.947552 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X339.190732 Y313.879273 Z2 E4150.979977 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 note=prime ramp
G1 X341.331494 Y314.64525 Z2 E4161.378089 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X343.543906 Y315.199431 Z2 E4171.808634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X345.799984 Y315.534088 Z2 E4182.239179 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X348.078 Y315.646 Z2 E4192.669723 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X350.356016 Y315.534088 Z2 E4203.100268 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X352.612094 Y315.199431 Z2 E4213.530813 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X354.824506 Y314.64525 Z2 E4223.961357 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X356.971946 Y313.876884 Z2 E4234.391902 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X359.033732 Y312.901732 Z2 E4244.822447 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X360.990008 Y311.729185 Z2 E4255.252991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X362.821934 Y310.370536 Z2 E4265.683536 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X364.511869 Y308.838869 Z2 E4276.114081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X366.043536 Y307.148934 Z2 E4286.544625 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X367.402185 Y305.317008 Z2 E4296.97517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X368.574732 Y303.360732 Z2 E4307.405715 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X369.549884 Y301.298946 Z2 E4317.836259 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X370.31825 Y299.151506 Z2 E4328.266804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X370.872431 Y296.939094 Z2 E4338.697349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X371.207088 Y294.683016 Z2 E4349.127893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X371.319 Y292.405 Z2 E4359.558438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X371.207088 Y290.126984 Z2 E4369.988983 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X370.872431 Y287.870906 Z2 E4380.419527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X370.31825 Y285.658494 Z2 E4390.850072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X369.549884 Y283.511054 Z2 E4401.280617 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X368.574732 Y281.449268 Z2 E4411.711161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X367.402185 Y279.492992 Z2 E4422.141706 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X366.043536 Y277.661066 Z2 E4432.572251 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X364.511869 Y275.971131 Z2 E4443.002795 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X362.821934 Y274.439464 Z2 E4453.43334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X360.990008 Y273.080815 Z2 E4463.863885 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X359.033732 Y271.908268 Z2 E4474.294429 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X356.971946 Y270.933116 Z2 E4484.724974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X354.824506 Y270.16475 Z2 E4495.155518 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X352.612094 Y269.610569 Z2 E4505.586063 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X350.356016 Y269.275912 Z2 E4516.016608 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X348.078 Y269.164 Z2 E4526.447152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X345.799984 Y269.275912 Z2 E4536.877697 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X343.543906 Y269.610569 Z2 E4547.308242 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X341.331494 Y270.16475 Z2 E4557.738786 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X339.184054 Y270.933116 Z2 E4568.169331 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X337.122268 Y271.908268 Z2 E4578.599876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X335.165992 Y273.080815 Z2 E4589.03042 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X333.334066 Y274.439464 Z2 E4599.460965 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X331.644131 Y275.971131 Z2 E4609.89151 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X330.112464 Y277.661066 Z2 E4620.322054 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X328.753815 Y279.492992 Z2 E4630.752599 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X328.465132 Y279.97463 Z2 E4633.320614 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X327.581268 Y281.449268 Z2.859618 E4642.111189 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=2 matz1=2.859618 note=collision lift
G1 X326.606116 Y283.511054 Z4 E4653.772893 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=2.859618 matz1=4 note=collision lift
G1 X325.83775 Y285.658494 Z4 E4664.203438 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=4 matz1=4 note=collision lift
G1 X325.283569 Y287.870906 Z2.859618 E4675.865141 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=4 matz1=2.859618 note=collision lift
G1 X325.031305 Y289.571534 Z2 E4684.655716 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=2.859618 matz1=2 note=collision lift
G1 X324.948912 Y290.126984 Z2 E4687.223731 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X324.837 Y292.405 Z2 E4697.654276 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X324.948912 Y294.683016 Z2 E4708.084821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X325.031305 Y295.238466 Z2 E4710.652836 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008
G1 X325.283569 Y296.939094 Z2.859618 E4719.443411 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=2 matz1=2.859618 note=collision lift
G1 X325.83775 Y299.151506 Z4 E4731.105115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=2.859618 matz1=4 note=collision lift
G1 X326.146999 Y300.015799 Z4 E4735.303159 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=4 matz1=4 note=collision lift
G1 X326.606116 Y301.298946 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=4 matz1=4 note=collision lift
G1 X327.581268 Y303.360732 Z2.859618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=4 matz1=2.859618 note=collision lift
G1 X328.081201 Y304.194819 Z2.3734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0008 matz0=2.859618 matz1=2.3734 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0008
G0 X328.081201 Y304.194819 Z6.3734 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0009 note=intra-page lift
G0 X335.505849 Y317.65216 Z6.3734 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0009 note=intra-page XY
G0 X335.505849 Y317.65216 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0009 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0009
G1 X334.483562 Y318.264895 Z2.910761 E4735.646154 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=2 matz1=2.910761 note=collision lift
G1 X333.461275 Y318.87763 Z3.821522 E4736.67514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=2.910761 matz1=3.821522 note=collision lift
G1 X333.260942 Y318.997705 Z4 E4736.957173 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=3.821522 matz1=4 note=collision lift
G1 X332.292233 Y319.716149 Z4 E4738.390115 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=4 matz1=4 note=collision lift
G1 X331.245324 Y320.49259 Z4 E4740.43735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=4 matz1=4 note=collision lift
G1 X331.158731 Y320.556811 Z3.946096 E4740.652833 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=4 matz1=3.946096 note=collision lift
G1 X331.108327 Y320.602495 Z3.912083 E4740.791081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=3.946096 matz1=3.912083 note=collision lift
G1 X330.114236 Y321.503486 Z3.241262 E4743.878038 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=3.912083 matz1=3.241262 note=collision lift
G1 X329.219462 Y322.314462 Z2.637461 E4747.243199 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=3.241262 matz1=2.637461 note=collision lift
G1 X329.129447 Y322.413778 Z2.70448 E4747.650984 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=2.637461 matz1=2.70448 note=collision lift
G1 X328.228457 Y323.407868 Z3.375301 E4752.109921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=2.70448 matz1=3.375301 note=collision lift
G1 X327.461811 Y324.253731 Z3.946096 E4756.444177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=3.375301 matz1=3.946096 note=collision lift
G1 X327.39759 Y324.340324 Z4 E4756.879158 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=3.946096 matz1=4 note=collision lift
G1 X327.336156 Y324.423158 Z4 E4757.254848 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=4 matz1=4 note=collision lift
G1 X326.442607 Y325.627969 Z4 E4763.085766 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=4 matz1=4 note=collision lift
G1 X325.902705 Y326.355942 Z4 E4766.941396 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=4 matz1=4 note=collision lift
G1 X325.62972 Y326.81139 Z3.734504 E4769.602673 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=4 matz1=3.734504 note=collision lift
G1 X324.55716 Y328.600849 Z2.691365 E4780.269952 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=3.734504 matz1=2.691365 note=collision lift
G1 X323.965967 Y329.850822 Z2 E4787.339948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 matz0=2.691365 matz1=2 note=collision lift
G1 X323.438133 Y330.966833 Z2 E4792.985829 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X322.556401 Y333.431108 Z2 E4804.955306 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X321.920457 Y335.969941 Z2 E4816.924784 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X321.536423 Y338.558883 Z2 E4828.894261 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X321.408 Y341.173 Z2 E4840.863739 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X321.536423 Y343.787117 Z2 E4852.833216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X321.920457 Y346.376059 Z2 E4864.802694 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X322.556401 Y348.914892 Z2 E4876.772171 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X323.438133 Y351.379167 Z2 E4888.741649 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X324.55716 Y353.745151 Z2 E4900.711126 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X325.902705 Y355.990058 Z2 E4912.680604 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X327.461811 Y358.092269 Z2 E4924.650081 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X329.219462 Y360.031538 Z2 E4936.619558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X331.158731 Y361.789189 Z2 E4948.589036 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X333.260942 Y363.348295 Z2 E4960.558513 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X335.505849 Y364.69384 Z2 E4972.527991 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X337.871833 Y365.812867 Z2 E4984.497468 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X340.336108 Y366.694599 Z2 E4996.466946 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X342.874941 Y367.330543 Z2 E5008.436423 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X345.463883 Y367.714577 Z2 E5020.405901 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X348.078 Y367.843 Z2 E5032.375378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X350.692117 Y367.714577 Z2 E5044.344856 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X353.281059 Y367.330543 Z2 E5056.314333 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X355.819892 Y366.694599 Z2 E5068.283811 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X358.284167 Y365.812867 Z2 E5080.253288 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X360.650151 Y364.69384 Z2 E5092.222766 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X362.895058 Y363.348295 Z2 E5104.192243 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X364.997269 Y361.789189 Z2 E5116.161721 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X366.936538 Y360.031538 Z2 E5128.131198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X368.694189 Y358.092269 Z2 E5140.100676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X370.253295 Y355.990058 Z2 E5152.070153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X371.59884 Y353.745151 Z2 E5164.039631 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X372.717867 Y351.379167 Z2 E5176.009108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X373.599599 Y348.914892 Z2 E5187.978586 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X374.235543 Y346.376059 Z2 E5199.948063 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X374.619577 Y343.787117 Z2 E5211.91754 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X374.748 Y341.173 Z2 E5223.887018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X374.619577 Y338.558883 Z2 E5235.856495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X374.235543 Y335.969941 Z2 E5247.825973 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X373.599599 Y333.431108 Z2 E5259.79545 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X372.717867 Y330.966833 Z2 E5271.764928 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X371.59884 Y328.600849 Z2 E5283.734405 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X370.253295 Y326.355942 Z2 E5295.703883 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X368.694189 Y324.253731 Z2 E5307.67336 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X366.936538 Y322.314462 Z2 E5319.642838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X364.997269 Y320.556811 Z2 E5331.612315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X362.895058 Y318.997705 Z2 E5343.581793 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X360.650151 Y317.65216 Z2 E5355.55127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X358.284167 Y316.533133 Z2 E5367.520748 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X355.819892 Y315.651401 Z2 E5379.490225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X353.281059 Y315.015457 Z2 E5391.459703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X350.692117 Y314.631423 Z2 E5403.42918 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X348.078 Y314.503 Z2 E5415.398658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X345.463883 Y314.631423 Z2 E5427.368135 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X342.874941 Y315.015457 Z2 E5439.337613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X340.336108 Y315.651401 Z2 E5451.30709 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X340.115278 Y315.730415 Z2 E5452.379702 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009
G1 X337.871833 Y316.533133 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
G1 X335.505849 Y317.65216 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0009 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0009
G0 X335.505849 Y317.65216 Z8.94731 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0010 note=intra-page lift
G0 X335.687126 Y318.158794 Z8.94731 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0010 note=intra-page XY
G0 X335.687126 Y318.158794 Z4.94731 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0010 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0010
G1 X335.152485 Y318.350091 Z5.407436 E5452.461129 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X335.152015 Y318.350314 Z5.407176 E5452.461259 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X334.605177 Y318.608949 Z5.881268 E5452.722697 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X334.468226 Y318.673722 Z6 E5452.816371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X334.467355 Y318.674134 Z6 E5452.816868 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X333.530096 Y319.117424 Z6 E5453.516044 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X333.29872 Y319.256105 Z6 E5453.751683 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X332.012127 Y320.02726 Z6 E5455.466658 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X331.990732 Y320.040084 Z6 E5455.500977 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X330.805956 Y320.918773 Z6 E5457.867624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X330.549216 Y321.109185 Z6 E5458.467927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X330.312049 Y321.32414 Z6 E5459.100272 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X330.312042 Y321.324146 Z6 E5459.100289 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X329.741922 Y321.840873 Z5.615281 E5460.954581 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X329.219809 Y322.314089 Z5.262957 E5462.850665 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X329.219433 Y322.31443 Z5.263211 E5462.852097 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X329.219431 Y322.314431 Z5.26321 E5462.852103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X329.21943 Y322.314433 Z5.263211 E5462.852109 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X329.219089 Y322.314809 Z5.262957 E5462.853542 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X328.791997 Y322.786032 Z5.58094 E5464.727527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X328.229146 Y323.407042 Z6 E5467.432615 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X328.229139 Y323.407051 Z6 E5467.432649 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X328.014185 Y323.644216 Z6 E5468.418006 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X327.869516 Y323.839279 Z6 E5469.186464 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X326.975967 Y325.04409 Z6 E5474.331391 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X326.945084 Y325.085732 Z6 E5474.521479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X326.200583 Y326.327856 Z6 E5480.162309 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X326.022424 Y326.625096 Z6 E5481.606968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X325.578991 Y327.562656 Z6 E5486.149311 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X325.578722 Y327.563226 Z6 E5486.152172 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X325.534472 Y327.656783 Z5.948296 E5486.679216 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X325.255091 Y328.247485 Z5.621849 E5490.01974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X324.650475 Y329.937274 Z4.724499 E5499.196162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
G1 X324.214399 Y331.678188 Z3.827149 E5508.372585 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=3.827149 note=collision lift
G1 X323.951062 Y333.453463 Z2.9298 E5517.549007 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=3.827149 matz1=2.9298 note=collision lift
G1 X323.863 Y335.246 Z2.03245 E5526.72543 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2.9298 matz1=2.03245 note=collision lift
G1 X323.866185 Y335.310822 Z2 E5527.057269 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2.03245 matz1=2 note=collision lift
G1 X323.951062 Y337.038537 Z2 E5534.968104 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X324.214399 Y338.813812 Z2 E5543.175746 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X324.650475 Y340.554726 Z2 E5551.383388 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X325.255091 Y342.244515 Z2 E5559.59103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X326.022424 Y343.866904 Z2 E5567.798671 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X326.945084 Y345.406268 Z2 E5576.006313 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X328.014185 Y346.847784 Z2 E5584.213955 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X329.219431 Y348.177569 Z2 E5592.421596 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X330.549216 Y349.382815 Z2 E5600.629238 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X331.990732 Y350.451916 Z2 E5608.83688 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X333.530096 Y351.374576 Z2 E5617.044521 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X335.152485 Y352.141909 Z2 E5625.252163 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X336.842274 Y352.746525 Z2 E5633.459805 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X338.583188 Y353.182601 Z2 E5641.667447 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X340.358463 Y353.445938 Z2 E5649.875088 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X342.151 Y353.534 Z2 E5658.08273 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X343.943537 Y353.445938 Z2 E5666.290372 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X345.718812 Y353.182601 Z2 E5674.498013 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X347.459726 Y352.746525 Z2 E5682.705655 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X349.149515 Y352.141909 Z2 E5690.913297 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X350.771904 Y351.374576 Z2 E5699.120938 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X352.311268 Y350.451916 Z2 E5707.32858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X353.752784 Y349.382815 Z2 E5715.536222 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X355.082569 Y348.177569 Z2 E5723.743864 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X356.287815 Y346.847784 Z2 E5731.951505 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X357.356916 Y345.406268 Z2 E5740.159147 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X358.279576 Y343.866904 Z2 E5748.366789 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X359.046909 Y342.244515 Z2 E5756.57443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X359.651525 Y340.554726 Z2 E5764.782072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X360.087601 Y338.813812 Z2 E5772.989714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X360.350938 Y337.038537 Z2 E5781.197355 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X360.439 Y335.246 Z2 E5789.404997 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X360.350938 Y333.453463 Z2 E5797.612639 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X360.087601 Y331.678188 Z2 E5805.820281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X359.651525 Y329.937274 Z2 E5814.027922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X359.046909 Y328.247485 Z2 E5822.235564 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X358.279576 Y326.625096 Z2 E5830.443206 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X357.356916 Y325.085732 Z2 E5838.650847 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X356.287815 Y323.644216 Z2 E5846.858489 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X355.082569 Y322.314431 Z2 E5855.066131 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X353.752784 Y321.109185 Z2 E5863.273772 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X352.311268 Y320.040084 Z2 E5871.481414 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X350.771904 Y319.117424 Z2 E5879.689056 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X349.149515 Y318.350091 Z2 E5887.896698 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X347.459726 Y317.745475 Z2 E5896.104339 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X345.718812 Y317.309399 Z2 E5904.311981 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X343.943537 Y317.046062 Z2 E5912.519623 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X342.151 Y316.958 Z2 E5920.727264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X341.4332 Y316.993263 Z2 E5924.013915 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010
G1 X340.358463 Y317.046062 Z2.538017 E5929.51575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2 matz1=2.538017 note=collision lift
G1 X340.018059 Y317.096556 Z2.710081 E5931.275303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2.538017 matz1=2.710081 note=collision lift
G1 X338.583188 Y317.309399 Z3.435366 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=2.710081 matz1=3.435366 note=collision lift
G1 X336.842274 Y317.745475 Z4.332716 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=3.435366 matz1=4 note=collision lift
G1 X335.687126 Y318.158794 Z4.946149 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0010 matz0=4 matz1=4 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0010
G0 X335.687126 Y318.158794 Z8.946149 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0011 note=intra-page lift
G0 X325.552235 Y277.36298 Z8.946149 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0011 note=intra-page XY
G0 X325.552235 Y277.36298 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0011 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0011
G1 X326.987646 Y276.927553 Z2 E5931.618298 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X327.33906 Y276.820953 Z2 E5931.806798 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X328.338077 Y276.286967 Z2 E5932.647283 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X328.985806 Y275.940748 Z2 E5933.401284 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X329.577582 Y275.45509 Z2 E5934.362259 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X330.429192 Y274.756192 Z2 E5936.058761 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X330.681884 Y274.448286 Z2 E5936.763225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X331.613748 Y273.312806 Z2 E5939.779228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X331.628406 Y273.285384 Z2 E5939.850181 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X332.335501 Y271.962502 Z2 E5943.623128 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X332.493953 Y271.66606 Z2 E5944.562687 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X332.831805 Y270.552308 Z2 E5948.082065 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X333.03598 Y269.879235 Z2 E5950.409135 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X333.114064 Y269.086431 Z2 E5953.226992 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X333.219 Y268.021 Z2 E5957.318575 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X333.17691 Y267.593653 Z2 E5959.057909 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X333.03598 Y266.162765 Z2 E5965.291005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X333.017928 Y266.103255 Z2 E5965.574817 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 note=prime ramp
G1 X332.493953 Y264.37594 Z2 E5973.829744 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X331.613748 Y262.729194 Z2 E5982.369072 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X330.429192 Y261.285808 Z2 E5990.908401 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X328.985806 Y260.101252 Z2 E5999.447729 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X327.33906 Y259.221047 Z2 E6007.987057 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X325.552235 Y258.67902 Z2 E6016.526386 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X323.694 Y258.496 Z2 E6025.065714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X321.835765 Y258.67902 Z2 E6033.605043 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X320.04894 Y259.221047 Z2 E6042.144371 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X318.402194 Y260.101252 Z2 E6050.683699 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X316.958808 Y261.285808 Z2 E6059.223028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X315.774252 Y262.729194 Z2 E6067.762356 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X315.019225 Y264.141749 Z2 E6075.087267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X314.894047 Y264.37594 Z2.132773 E6076.445027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2 matz1=2.132773 note=collision lift
G1 X314.35202 Y266.162765 Z3.066387 E6085.992286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2.132773 matz1=3.066387 note=collision lift
G1 X314.169 Y268.021 Z4 E6095.539546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=3.066387 matz1=4 note=collision lift
G1 X314.35202 Y269.879235 Z4 E6104.078874 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=4 matz1=4 note=collision lift
G1 X314.894047 Y271.66606 Z3.066387 E6113.626133 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=4 matz1=3.066387 note=collision lift
G1 X315.774252 Y273.312806 Z2.132773 E6123.173393 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=3.066387 matz1=2.132773 note=collision lift
G1 X315.942713 Y273.518077 Z2 E6124.531153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2.132773 matz1=2 note=collision lift
G1 X316.958808 Y274.756192 Z2 E6131.856064 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X318.196923 Y275.772287 Z2 E6139.180974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011
G1 X318.402194 Y275.940748 Z2.132773 E6140.538735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2 matz1=2.132773 note=collision lift
G1 X320.04894 Y276.820953 Z3.066387 E6150.085994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=2.132773 matz1=3.066387 note=collision lift
G1 X320.941206 Y277.091618 Z3.532594 E6154.853498 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=3.066387 matz1=3.532594 note=collision lift
G1 X321.835765 Y277.36298 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=3.532594 matz1=4 note=collision lift
G1 X323.694 Y277.546 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=4 matz1=4 note=collision lift
G1 X325.552235 Y277.36298 Z3.066387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0011 matz0=4 matz1=3.066387 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0011
G0 X325.552235 Y277.36298 Z7.066387 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0012 note=intra-page lift
G0 X333.260942 Y265.812295 Z7.066387 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0012 note=intra-page XY
G0 X333.260942 Y265.812295 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0012 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0012
G1 X334.547535 Y266.583449 Z2 E6155.196493 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X335.505849 Y267.15784 Z2 E6155.897743 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X335.851833 Y267.321478 Z2 E6156.225479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X337.207817 Y267.962811 Z2 E6157.940454 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X337.871833 Y268.276867 Z2 E6159.030478 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X338.592548 Y268.534743 Z2 E6160.34142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X340.004864 Y269.040078 Z2 E6163.428377 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X340.336108 Y269.158599 Z2 E6164.251704 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X341.449889 Y269.437586 Z2 E6167.201323 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X342.874941 Y269.794543 Z2 E6171.561419 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X342.905527 Y269.79908 Z2 E6171.66026 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X344.389292 Y270.019176 Z2 E6176.805187 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X345.463883 Y270.178577 Z2 E6180.959624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X345.877036 Y270.198874 Z2 E6182.636105 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X347.375229 Y270.272475 Z2 E6189.153012 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 note=prime ramp
G1 X348.078 Y270.307 Z2 E6192.370849 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X350.692117 Y270.178577 Z2 E6204.340326 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X353.281059 Y269.794543 Z2 E6216.309804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X355.819892 Y269.158599 Z2 E6228.279281 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X358.284167 Y268.276867 Z2 E6240.248759 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X360.650151 Y267.15784 Z2 E6252.218236 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X362.895058 Y265.812295 Z2 E6264.187714 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X364.997269 Y264.253189 Z2 E6276.157191 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X366.936538 Y262.495538 Z2 E6288.126669 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X368.694189 Y260.556269 Z2 E6300.096146 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X370.253295 Y258.454058 Z2 E6312.065624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X371.59884 Y256.209151 Z2 E6324.035101 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X372.717867 Y253.843167 Z2 E6336.004578 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X373.599599 Y251.378892 Z2 E6347.974056 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X374.235543 Y248.840059 Z2 E6359.943533 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X374.619577 Y246.251117 Z2 E6371.913011 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X374.748 Y243.637 Z2 E6383.882488 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X374.619577 Y241.022883 Z2 E6395.851966 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X374.235543 Y238.433941 Z2 E6407.821443 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X373.599599 Y235.895108 Z2 E6419.790921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X372.717867 Y233.430833 Z2 E6431.760398 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X371.59884 Y231.064849 Z2 E6443.729876 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X370.253295 Y228.819942 Z2 E6455.699353 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X368.694189 Y226.717731 Z2 E6467.668831 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X366.936538 Y224.778462 Z2 E6479.638308 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X364.997269 Y223.020811 Z2 E6491.607786 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X362.895058 Y221.461705 Z2 E6503.577263 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X360.650151 Y220.11616 Z2 E6515.546741 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X358.284167 Y218.997133 Z2 E6527.516218 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X355.819892 Y218.115401 Z2 E6539.485696 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X353.281059 Y217.479457 Z2 E6551.455173 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X350.692117 Y217.095423 Z2 E6563.424651 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X348.078 Y216.967 Z2 E6575.394128 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X345.463883 Y217.095423 Z2 E6587.363606 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X342.874941 Y217.479457 Z2 E6599.333083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X340.336108 Y218.115401 Z2 E6611.30256 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X337.871833 Y218.997133 Z2 E6623.272038 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X335.505849 Y220.11616 Z2 E6635.241515 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X333.260942 Y221.461705 Z2 E6647.210993 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X331.158731 Y223.020811 Z2 E6659.18047 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X329.219462 Y224.778462 Z2 E6671.149948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X327.461811 Y226.717731 Z2 E6683.119425 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X325.902705 Y228.819942 Z2 E6695.088903 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X324.55716 Y231.064849 Z2 E6707.05838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X323.438133 Y233.430833 Z2 E6719.027858 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X322.556401 Y235.895108 Z2 E6730.997335 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X321.920457 Y238.433941 Z2 E6742.966813 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X321.536423 Y241.022883 Z2 E6754.93629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X321.408 Y243.637 Z2 E6766.905768 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X321.536423 Y246.251117 Z2 E6778.875245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X321.920457 Y248.840059 Z2 E6790.844723 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X322.556401 Y251.378892 Z2 E6802.8142 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X323.438133 Y253.843167 Z2 E6814.783678 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X323.965967 Y254.959178 Z2 E6820.429558 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012
G1 X324.55716 Y256.209151 Z2.691365 E6827.499554 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=2 matz1=2.691365 note=collision lift
G1 X325.902705 Y258.454058 Z4 E6840.881837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=2.691365 matz1=4 note=collision lift
G1 X327.39759 Y260.469676 Z4 E6852.358278 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=4 matz1=4 note=collision lift
G1 X327.461811 Y260.556269 Z3.946096 E6852.90951 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=4 matz1=3.946096 note=collision lift
G1 X329.219462 Y262.495538 Z2.637461 E6866.291792 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=3.946096 matz1=2.637461 note=collision lift
G1 X329.588065 Y262.82962 Z2.886197 E6868.835405 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=2.637461 matz1=2.886197 note=collision lift
G1 X331.158731 Y264.253189 Z3.946096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=2.886197 matz1=3.946096 note=collision lift
G1 X331.245324 Y264.31741 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=3.946096 matz1=4 note=collision lift
G1 X333.260942 Y265.812295 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0012 matz0=4 matz1=4 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0012
G0 X333.260942 Y265.812295 Z10 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0013 note=intra-page lift
G0 X333.384871 Y265.605531 Z10 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0013 note=intra-page XY
G0 X333.384871 Y265.605531 Z6 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0013 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0013
G1 X333.530096 Y265.692576 Z6 E6868.839775 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X334.468226 Y266.136278 Z6 E6869.057519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X334.705067 Y266.248296 Z5.869002 E6869.1784 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X335.152485 Y266.459909 Z5.621533 E6869.478143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X335.949694 Y266.745155 Z5.198182 E6870.207385 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X336.842274 Y267.064525 Z4.724184 E6871.348068 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X337.224121 Y267.160173 Z4.527361 E6871.922361 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=3.962018 note=collision lift
G1 X338.525555 Y267.486165 Z3.856541 E6874.323327 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=3.962018 matz1=3.832567 note=collision lift
G1 X338.583188 Y267.500601 Z3.826834 E6874.445514 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=3.832567 matz1=3.826834 note=collision lift
G1 X339.851537 Y267.688743 Z3.185721 E6877.410283 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=3.826834 matz1=3.185721 note=collision lift
G1 X340.358463 Y267.763938 Z2.929485 E6878.770481 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=3.185721 matz1=2.929485 note=collision lift
G1 X341.186632 Y267.804624 Z2.5149 E6881.18323 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=2.929485 matz1=2.5149 note=collision lift
G1 X342.151 Y267.852 Z2.032135 E6884.322968 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=2.5149 matz1=2.032135 note=collision lift
G1 X342.215192 Y267.848846 Z2 E6884.544574 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=2.032135 matz1=2 note=collision lift
G1 X342.56342 Y267.831739 Z2 E6885.642167 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X343.943537 Y267.763938 Z2 E6890.356708 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X344.060476 Y267.746592 Z2 E6890.787094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X345.544241 Y267.526496 Z2 E6896.618011 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X345.718812 Y267.500601 Z2 E6897.349143 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X347.002667 Y267.179012 Z2 E6903.134919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 note=prime ramp
G1 X347.459726 Y267.064525 Z2 E6905.289751 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X349.149515 Y266.459909 Z2 E6913.497393 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X350.771904 Y265.692576 Z2 E6921.705035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X352.311268 Y264.769916 Z2 E6929.912676 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X353.752784 Y263.700815 Z2 E6938.120318 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X355.082569 Y262.495569 Z2 E6946.32796 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X356.287815 Y261.165784 Z2 E6954.535602 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X357.356916 Y259.724268 Z2 E6962.743243 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X358.279576 Y258.184904 Z2 E6970.950885 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X359.046909 Y256.562515 Z2 E6979.158527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X359.651525 Y254.872726 Z2 E6987.366168 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X360.087601 Y253.131812 Z2 E6995.57381 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X360.350938 Y251.356537 Z2 E7003.781452 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X360.439 Y249.564 Z2 E7011.989093 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X360.350938 Y247.771463 Z2 E7020.196735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X360.087601 Y245.996188 Z2 E7028.404377 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X359.651525 Y244.255274 Z2 E7036.612019 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X359.046909 Y242.565485 Z2 E7044.81966 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X358.279576 Y240.943096 Z2 E7053.027302 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X357.356916 Y239.403732 Z2 E7061.234944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X356.287815 Y237.962216 Z2 E7069.442585 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X355.082569 Y236.632431 Z2 E7077.650227 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X353.752784 Y235.427185 Z2 E7085.857869 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X352.311268 Y234.358084 Z2 E7094.06551 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X350.771904 Y233.435424 Z2 E7102.273152 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X349.149515 Y232.668091 Z2 E7110.480794 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X347.459726 Y232.063475 Z2 E7118.688436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X345.718812 Y231.627399 Z2 E7126.896077 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X343.943537 Y231.364062 Z2 E7135.103719 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X342.151 Y231.276 Z2 E7143.311361 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X340.358463 Y231.364062 Z2 E7151.519002 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X338.583188 Y231.627399 Z2 E7159.726644 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X336.842274 Y232.063475 Z2 E7167.934286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X335.152485 Y232.668091 Z2 E7176.141927 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X333.530096 Y233.435424 Z2 E7184.349569 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X331.990732 Y234.358084 Z2 E7192.557211 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X330.549216 Y235.427185 Z2 E7200.764853 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X329.219431 Y236.632431 Z2 E7208.972494 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X328.014185 Y237.962216 Z2 E7217.180136 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X326.945084 Y239.403732 Z2 E7225.387778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X326.022424 Y240.943096 Z2 E7233.595419 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X325.255091 Y242.565485 Z2 E7241.803061 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X324.650475 Y244.255274 Z2 E7250.010703 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X324.214399 Y245.996188 Z2 E7258.218344 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X323.951062 Y247.771463 Z2 E7266.425986 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X323.866185 Y249.499178 Z2 E7274.336822 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013
G1 X323.863 Y249.564 Z2.03245 E7274.668661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=2 matz1=2.03245 note=collision lift
G1 X323.951062 Y251.356537 Z2.9298 E7283.845083 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=2.03245 matz1=2.9298 note=collision lift
G1 X324.214399 Y253.131812 Z3.827149 E7293.021506 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=2.9298 matz1=3.827149 note=collision lift
G1 X324.650475 Y254.872726 Z4.724499 E7302.197928 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=3.827149 matz1=4 note=collision lift
G1 X325.255091 Y256.562515 Z5.621849 E7311.374351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X325.578722 Y257.246774 Z6 E7315.243958 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X325.578991 Y257.247344 Z6 E7315.246842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X326.022424 Y258.184904 Z6 E7319.989941 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X326.945084 Y259.724268 Z6 E7328.197583 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X328.014185 Y261.165784 Z6 E7336.405225 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X328.229139 Y261.402949 Z6 E7337.869045 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X328.229146 Y261.402958 Z6 E7337.869096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X329.219089 Y262.495191 Z5.262957 E7345.406245 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X329.21943 Y262.495567 Z5.263211 E7345.408838 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X329.219431 Y262.495569 Z5.26321 E7345.408849 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X329.219433 Y262.49557 Z5.263211 E7345.40886 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X329.219809 Y262.495911 Z5.262957 E7345.411453 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X329.477123 Y262.729127 Z5.436594 E7347.187095 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X330.312042 Y263.485854 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X330.312051 Y263.485861 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X330.549216 Y263.700815 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X331.990732 Y264.769916 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
G1 X333.384871 Y265.605531 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0013 matz0=4 matz1=4 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0013
G0 X333.384871 Y265.605531 Z10 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0014 note=intra-page lift
G0 X318.634185 Y256.549008 Z10 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0014 note=intra-page XY
G0 X318.634185 Y256.549008 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0014 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0014
G1 X319.405339 Y255.262415 Z2 E7347.530091 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X319.806732 Y254.592732 Z2 E7347.980082 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X320.114245 Y253.94255 Z2 E7348.559076 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X320.755578 Y252.586566 Z2 E7350.274052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X320.781884 Y252.530946 Z2 E7350.359043 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X321.266491 Y251.17656 Z2 E7352.675018 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X321.55025 Y250.383506 Z2 E7354.323977 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X321.710061 Y249.745508 Z2 E7355.761974 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.074531 Y248.290461 Z2 E7359.534921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.104431 Y248.171094 Z2 E7359.874886 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.306471 Y246.809052 Z2 E7363.993857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.439088 Y245.915016 Z2 E7367.011768 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.468341 Y245.319553 Z2 E7369.138785 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.541943 Y243.821359 Z2 E7374.969702 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.551 Y243.637 Z2 E7375.734624 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.486455 Y242.323166 Z2 E7381.48661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=prime ramp
G1 X322.439088 Y241.358984 Z2 E7385.901394 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X322.104431 Y239.102906 Z2 E7396.331938 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X321.55025 Y236.890494 Z2 E7406.762483 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X320.781884 Y234.743054 Z2 E7417.193028 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X319.806732 Y232.681268 Z2 E7427.623572 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X318.634185 Y230.724992 Z2 E7438.054117 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X317.275536 Y228.893066 Z2 E7448.484662 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X315.743869 Y227.203131 Z2 E7458.915206 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X314.053934 Y225.671464 Z2 E7469.345751 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X312.222008 Y224.312815 Z2 E7479.776296 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X310.265732 Y223.140268 Z2 E7490.20684 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X308.203946 Y222.165116 Z2 E7500.637385 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X306.056506 Y221.39675 Z2 E7511.06793 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X303.844094 Y220.842569 Z2 E7521.498474 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X301.588016 Y220.507912 Z2 E7531.929019 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X299.31 Y220.396 Z2 E7542.359564 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X297.031984 Y220.507912 Z2 E7552.790108 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X294.775906 Y220.842569 Z2 E7563.220653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X292.563494 Y221.39675 Z2 E7573.651198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X290.416054 Y222.165116 Z2 E7584.081742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X288.354268 Y223.140268 Z2 E7594.512287 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X286.397992 Y224.312815 Z2 E7604.942832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X284.566066 Y225.671464 Z2 E7615.373376 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X282.876131 Y227.203131 Z2 E7625.803921 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X281.344464 Y228.893066 Z2 E7636.234466 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X279.985815 Y230.724992 Z2 E7646.66501 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X278.813268 Y232.681268 Z2 E7657.095555 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X277.838116 Y234.743054 Z2 E7667.5261 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X277.06975 Y236.890494 Z2 E7677.956644 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X276.515569 Y239.102906 Z2 E7688.387189 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X276.180912 Y241.358984 Z2 E7698.817734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X276.069 Y243.637 Z2 E7709.248278 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X276.180912 Y245.915016 Z2 E7719.678823 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X276.515569 Y248.171094 Z2 E7730.109367 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X277.06975 Y250.383506 Z2 E7740.539912 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X277.838116 Y252.530946 Z2 E7750.970457 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X278.813268 Y254.592732 Z2 E7761.401001 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X279.985815 Y256.549008 Z2 E7771.831546 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X281.344464 Y258.380934 Z2 E7782.262091 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X282.876131 Y260.070869 Z2 E7792.692635 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X284.566066 Y261.602536 Z2 E7803.12318 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X286.397992 Y262.961185 Z2 E7813.553725 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X286.87963 Y263.249868 Z2 E7816.12174 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X288.354268 Y264.133732 Z2.859618 E7824.912315 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=2 matz1=2.859618 note=collision lift
G1 X290.416054 Y265.108884 Z4 E7836.574019 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=2.859618 matz1=4 note=collision lift
G1 X292.563494 Y265.87725 Z4 E7847.004563 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X294.775906 Y266.431431 Z2.859618 E7858.666267 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=2.859618 note=collision lift
G1 X296.476534 Y266.683695 Z2 E7867.456842 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=2.859618 matz1=2 note=collision lift
G1 X297.031984 Y266.766088 Z2 E7870.024857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X298.413019 Y266.833934 Z2 E7876.348321 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X299.31 Y266.878 Z2.449031 E7880.940177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=2 matz1=2.449031 note=collision lift
G1 X301.588016 Y266.766088 Z3.589413 E7892.60188 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=2.449031 matz1=3.589413 note=collision lift
G1 X303.844094 Y266.431431 Z4.729795 E7904.263584 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=3.589413 matz1=4 note=collision lift
G1 X304.577243 Y266.247787 Z5.107694 E7908.128035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X304.660616 Y266.226903 Z5.140532 E7908.548817 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X304.662799 Y266.226356 Z5.139407 E7908.560322 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X304.738205 Y266.207468 Z5.151101 E7908.919826 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X304.74399 Y266.206019 Z5.154083 E7908.950322 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X304.903797 Y266.165989 Z5.153496 E7909.703744 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X304.910738 Y266.16425 Z5.157073 E7909.74033 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X305.243882 Y266.080802 Z5.107555 E7911.327198 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X305.244233 Y266.080714 Z5.107737 E7911.329049 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X305.650369 Y265.978982 Z5.01098 E7913.294268 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X305.654692 Y265.9779 Z5.008752 E7913.317052 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X306.056506 Y265.87725 Z4.882008 E7915.298123 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X306.068912 Y265.872811 Z4.875419 E7915.365495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X306.233017 Y265.814094 Z4.820932 E7916.200625 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X306.234998 Y265.813385 Z4.819879 E7916.211386 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X306.35869 Y265.769127 Z4.775133 E7916.846076 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X306.366875 Y265.766198 Z4.77948 E7916.890527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X306.949662 Y265.557674 Z4.530429 E7919.941789 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X307.23272 Y265.456394 Z4.380112 E7921.478943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X307.240749 Y265.453522 Z4.376011 E7921.522215 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X307.241055 Y265.453412 Z4.376174 E7921.523879 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X307.949423 Y265.199954 Z4 E7925.370682 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X308.203946 Y265.108884 Z4 E7926.606949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=4 note=collision lift
G1 X310.265732 Y264.133732 Z2.859618 E7938.268653 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=4 matz1=2.859618 note=collision lift
G1 X311.74037 Y263.249868 Z2 E7947.059228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 matz0=2.859618 matz1=2 note=collision lift
G1 X312.222008 Y262.961185 Z2 E7949.627243 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X314.053934 Y261.602536 Z2 E7960.057788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X315.418982 Y260.365329 Z2 E7968.483079 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014
G1 X315.743869 Y260.070869 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X317.275536 Y258.380934 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
G1 X318.634185 Y256.549008 Z2 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0014 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0014
G0 X318.634185 Y256.549008 Z6 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0015 note=intra-page lift
G0 X284.26798 Y266.162765 Z6 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0015 note=intra-page XY
G0 X284.26798 Y266.162765 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0015 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0015
G1 X283.832553 Y264.727354 Z2 E7968.826074 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X283.725953 Y264.37594 Z2 E7969.014574 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X283.191967 Y263.376923 Z2 E7969.85506 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X282.845748 Y262.729194 Z2 E7970.60906 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X282.36009 Y262.137418 Z2 E7971.570035 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X281.661192 Y261.285808 Z2 E7973.266537 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X281.353286 Y261.033116 Z2 E7973.971001 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X280.217806 Y260.101252 Z2 E7976.987005 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X280.190384 Y260.086594 Z2 E7977.057958 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X278.867502 Y259.379499 Z2 E7980.830904 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X278.57106 Y259.221047 Z2 E7981.770463 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X277.457308 Y258.883195 Z2 E7985.289841 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X276.784235 Y258.67902 Z2 E7987.616911 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X275.991431 Y258.600936 Z2 E7990.434768 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X274.926 Y258.496 Z2 E7994.526351 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X274.498653 Y258.53809 Z2 E7996.265686 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X273.067765 Y258.67902 Z2 E8002.498781 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X273.008255 Y258.697072 Z2 E8002.782593 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 note=prime ramp
G1 X271.28094 Y259.221047 Z2 E8011.03752 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X269.634194 Y260.101252 Z2 E8019.576848 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X268.190808 Y261.285808 Z2 E8028.116177 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X267.006252 Y262.729194 Z2 E8036.655505 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X266.126047 Y264.37594 Z2 E8045.194833 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X265.58402 Y266.162765 Z2 E8053.734162 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X265.401 Y268.021 Z2 E8062.27349 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X265.58402 Y269.879235 Z2 E8070.812819 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X266.126047 Y271.66606 Z2 E8079.352147 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X267.006252 Y273.312806 Z2 E8087.891475 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X268.190808 Y274.756192 Z2 E8096.430804 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X269.634194 Y275.940748 Z2 E8104.970132 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X271.046749 Y276.695775 Z2 E8112.295043 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X271.28094 Y276.820953 Z2.132773 E8113.652803 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2 matz1=2.132773 note=collision lift
G1 X273.067765 Y277.36298 Z3.066387 E8123.200062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.132773 matz1=3.066387 note=collision lift
G1 X274.926 Y277.546 Z4 E8132.747322 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.066387 matz1=4 note=collision lift
G1 X276.784235 Y277.36298 Z4 E8141.28665 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=4 note=collision lift
G1 X278.57106 Y276.820953 Z3.066387 E8150.833909 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=3.066387 note=collision lift
G1 X280.217806 Y275.940748 Z2.132773 E8160.381169 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.066387 matz1=2.132773 note=collision lift
G1 X280.423077 Y275.772287 Z2 E8161.738929 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.132773 matz1=2 note=collision lift
G1 X281.661192 Y274.756192 Z2 E8169.06384 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X282.677287 Y273.518077 Z2 E8176.388751 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015
G1 X282.845748 Y273.312806 Z2.132773 E8177.746511 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2 matz1=2.132773 note=collision lift
G1 X283.725953 Y271.66606 Z3.066387 E8187.29377 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=2.132773 matz1=3.066387 note=collision lift
G1 X283.996618 Y270.773794 Z3.532594 E8192.061274 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.066387 matz1=3.532594 note=collision lift
G1 X284.26798 Y269.879235 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=3.532594 matz1=4 note=collision lift
G1 X284.451 Y268.021 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=4 note=collision lift
G1 X284.26798 Y266.162765 Z3.066387 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0015 matz0=4 matz1=3.066387 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0015
G0 X284.26798 Y266.162765 Z7.066387 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0016 note=intra-page lift
G0 X272.717295 Y258.454058 Z7.066387 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0016 note=intra-page XY
G0 X272.717295 Y258.454058 Z2 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0016 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0016
G1 X273.488449 Y257.167465 Z2 E8192.404269 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X274.06284 Y256.209151 Z2 E8193.105519 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X274.226478 Y255.863167 Z2 E8193.433255 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X274.867811 Y254.507183 Z2 E8195.148231 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X275.181867 Y253.843167 Z2 E8196.238254 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X275.439743 Y253.122452 Z2 E8197.549197 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X275.945078 Y251.710136 Z2 E8200.636153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X276.063599 Y251.378892 Z2 E8201.45948 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X276.342586 Y250.265111 Z2 E8204.409099 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X276.699543 Y248.840059 Z2 E8208.769195 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X276.70408 Y248.809473 Z2 E8208.868036 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X276.924176 Y247.325708 Z2 E8214.012963 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X277.083577 Y246.251117 Z2 E8218.1674 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X277.103874 Y245.837964 Z2 E8219.843881 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X277.177475 Y244.339771 Z2 E8226.360788 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 note=prime ramp
G1 X277.212 Y243.637 Z2 E8229.578625 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X277.083577 Y241.022883 Z2 E8241.548102 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X276.699543 Y238.433941 Z2 E8253.51758 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X276.063599 Y235.895108 Z2 E8265.487057 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X275.181867 Y233.430833 Z2 E8277.456535 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X274.06284 Y231.064849 Z2 E8289.426012 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X272.717295 Y228.819942 Z2 E8301.39549 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X271.158189 Y226.717731 Z2 E8313.364967 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X269.400538 Y224.778462 Z2 E8325.334445 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X267.461269 Y223.020811 Z2 E8337.303922 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X265.359058 Y221.461705 Z2 E8349.2734 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X263.114151 Y220.11616 Z2 E8361.242877 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X260.748167 Y218.997133 Z2 E8373.212355 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X258.283892 Y218.115401 Z2 E8385.181832 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X255.745059 Y217.479457 Z2 E8397.15131 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X253.156117 Y217.095423 Z2 E8409.120787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X250.542 Y216.967 Z2 E8421.090264 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X247.927883 Y217.095423 Z2 E8433.059742 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X245.338941 Y217.479457 Z2 E8445.029219 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X242.800108 Y218.115401 Z2 E8456.998697 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X240.335833 Y218.997133 Z2 E8468.968174 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X237.969849 Y220.11616 Z2 E8480.937652 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X235.724942 Y221.461705 Z2 E8492.907129 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X233.622731 Y223.020811 Z2 E8504.876607 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X231.683462 Y224.778462 Z2 E8516.846084 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X229.925811 Y226.717731 Z2 E8528.815562 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X228.366705 Y228.819942 Z2 E8540.785039 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X227.02116 Y231.064849 Z2 E8552.754517 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X225.902133 Y233.430833 Z2 E8564.723994 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X225.020401 Y235.895108 Z2 E8576.693472 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X224.384457 Y238.433941 Z2 E8588.662949 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X224.000423 Y241.022883 Z2 E8600.632427 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X223.872 Y243.637 Z2 E8612.601904 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X224.000423 Y246.251117 Z2 E8624.571382 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X224.384457 Y248.840059 Z2 E8636.540859 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X225.020401 Y251.378892 Z2 E8648.510337 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X225.902133 Y253.843167 Z2 E8660.479814 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X227.02116 Y256.209151 Z2 E8672.449292 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X228.366705 Y258.454058 Z2 E8684.418769 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X229.925811 Y260.556269 Z2 E8696.388246 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X231.683462 Y262.495538 Z2 E8708.357724 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X233.622731 Y264.253189 Z2 E8720.327201 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X235.724942 Y265.812295 Z2 E8732.296679 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X237.969849 Y267.15784 Z2 E8744.266156 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X240.335833 Y268.276867 Z2 E8756.235634 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X242.800108 Y269.158599 Z2 E8768.205111 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X245.338941 Y269.794543 Z2 E8780.174589 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X247.927883 Y270.178577 Z2 E8792.144066 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X250.542 Y270.307 Z2 E8804.113544 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X253.156117 Y270.178577 Z2 E8816.083021 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X255.745059 Y269.794543 Z2 E8828.052499 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X258.283892 Y269.158599 Z2 E8840.021976 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X260.748167 Y268.276867 Z2 E8851.991454 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X261.864178 Y267.749033 Z2 E8857.637334 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016
G1 X263.114151 Y267.15784 Z2.691365 E8864.70733 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2 matz1=2.691365 note=collision lift
G1 X265.359058 Y265.812295 Z4 E8878.089613 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2.691365 matz1=4 note=collision lift
G1 X267.374676 Y264.31741 Z4 E8889.566054 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=4 matz1=4 note=collision lift
G1 X267.461269 Y264.253189 Z3.946096 E8890.117286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=4 matz1=3.946096 note=collision lift
G1 X269.400538 Y262.495538 Z2.637461 E8903.499568 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=3.946096 matz1=2.637461 note=collision lift
G1 X269.73462 Y262.126935 Z2.886197 E8906.043181 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2.637461 matz1=2.886197 note=collision lift
G1 X271.158189 Y260.556269 Z3.946096 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=2.886197 matz1=3.946096 note=collision lift
G1 X271.22241 Y260.469676 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=3.946096 matz1=4 note=collision lift
G1 X272.717295 Y258.454058 Z4 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0016 matz0=4 matz1=4 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0016
G0 X272.717295 Y258.454058 Z10 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=stroke-0017 note=intra-page lift
G0 X272.510531 Y258.330129 Z10 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=stroke-0017 note=intra-page XY
G0 X272.510531 Y258.330129 Z6 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=stroke-0017 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=stroke-0017
G1 X272.597576 Y258.184904 Z6 E8906.047551 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X273.041278 Y257.246774 Z6 E8906.265296 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X273.153296 Y257.009933 Z5.869002 E8906.386176 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X273.364909 Y256.562515 Z5.621533 E8906.685919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X273.650155 Y255.765306 Z5.198182 E8907.415161 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X273.969525 Y254.872726 Z4.724184 E8908.555845 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X274.065173 Y254.490879 Z4.527361 E8909.130137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=3.962018 note=collision lift
G1 X274.391165 Y253.189445 Z3.856541 E8911.531103 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=3.962018 matz1=3.832567 note=collision lift
G1 X274.405601 Y253.131812 Z3.826834 E8911.65329 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=3.832567 matz1=3.826834 note=collision lift
G1 X274.593743 Y251.863463 Z3.185721 E8914.618059 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=3.826834 matz1=3.185721 note=collision lift
G1 X274.668938 Y251.356537 Z2.929485 E8915.978257 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=3.185721 matz1=2.929485 note=collision lift
G1 X274.709624 Y250.528368 Z2.5149 E8918.391006 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=2.929485 matz1=2.5149 note=collision lift
G1 X274.757 Y249.564 Z2.032135 E8921.530744 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=2.5149 matz1=2.032135 note=collision lift
G1 X274.753846 Y249.499808 Z2 E8921.75235 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=2.032135 matz1=2 note=collision lift
G1 X274.736739 Y249.15158 Z2 E8922.849943 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X274.668938 Y247.771463 Z2 E8927.564484 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X274.651592 Y247.654524 Z2 E8927.99487 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X274.431496 Y246.170759 Z2 E8933.825787 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X274.405601 Y245.996188 Z2 E8934.556919 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X274.084012 Y244.712333 Z2 E8940.342695 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 note=prime ramp
G1 X273.969525 Y244.255274 Z2 E8942.497527 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X273.364909 Y242.565485 Z2 E8950.705169 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X272.597576 Y240.943096 Z2 E8958.912811 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X271.674916 Y239.403732 Z2 E8967.120453 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X270.605815 Y237.962216 Z2 E8975.328094 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X269.400569 Y236.632431 Z2 E8983.535736 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X268.070784 Y235.427185 Z2 E8991.743378 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X266.629268 Y234.358084 Z2 E8999.951019 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X265.089904 Y233.435424 Z2 E9008.158661 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X263.467515 Y232.668091 Z2 E9016.366303 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X261.777726 Y232.063475 Z2 E9024.573944 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X260.036812 Y231.627399 Z2 E9032.781586 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X258.261537 Y231.364062 Z2 E9040.989228 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X256.469 Y231.276 Z2 E9049.19687 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X254.676463 Y231.364062 Z2 E9057.404511 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X252.901188 Y231.627399 Z2 E9065.612153 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X251.160274 Y232.063475 Z2 E9073.819795 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X249.470485 Y232.668091 Z2 E9082.027436 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X247.848096 Y233.435424 Z2 E9090.235078 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X246.308732 Y234.358084 Z2 E9098.44272 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X244.867216 Y235.427185 Z2 E9106.650361 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X243.537431 Y236.632431 Z2 E9114.858003 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X242.332185 Y237.962216 Z2 E9123.065645 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X241.263084 Y239.403732 Z2 E9131.273287 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X240.340424 Y240.943096 Z2 E9139.480928 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X239.573091 Y242.565485 Z2 E9147.68857 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X238.968475 Y244.255274 Z2 E9155.896212 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X238.532399 Y245.996188 Z2 E9164.103853 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X238.269062 Y247.771463 Z2 E9172.311495 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X238.181 Y249.564 Z2 E9180.519137 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X238.269062 Y251.356537 Z2 E9188.726778 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X238.532399 Y253.131812 Z2 E9196.93442 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X238.968475 Y254.872726 Z2 E9205.142062 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X239.573091 Y256.562515 Z2 E9213.349704 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X240.340424 Y258.184904 Z2 E9221.557345 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X241.263084 Y259.724268 Z2 E9229.764987 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X242.332185 Y261.165784 Z2 E9237.972629 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X243.537431 Y262.495569 Z2 E9246.18027 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X244.867216 Y263.700815 Z2 E9254.387912 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X246.308732 Y264.769916 Z2 E9262.595554 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X247.848096 Y265.692576 Z2 E9270.803195 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X249.470485 Y266.459909 Z2 E9279.010837 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X251.160274 Y267.064525 Z2 E9287.218479 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X252.901188 Y267.500601 Z2 E9295.426121 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X254.676463 Y267.763938 Z2 E9303.633762 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X256.404178 Y267.848815 Z2 E9311.544598 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017
G1 X256.469 Y267.852 Z2.03245 E9311.876437 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=2 matz1=2.03245 note=collision lift
G1 X258.261537 Y267.763938 Z2.9298 E9321.05286 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=2.03245 matz1=2.9298 note=collision lift
G1 X260.036812 Y267.500601 Z3.827149 E9330.229282 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=2.9298 matz1=3.827149 note=collision lift
G1 X261.777726 Y267.064525 Z4.724499 E9339.405704 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=3.827149 matz1=4 note=collision lift
G1 X263.467515 Y266.459909 Z5.621849 E9348.582127 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X264.151774 Y266.136278 Z6 E9352.451735 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X264.152344 Y266.136009 Z6 E9352.454618 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X265.089904 Y265.692576 Z6 E9357.197717 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X266.629268 Y264.769916 Z6 E9365.405359 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X268.070784 Y263.700815 Z6 E9373.613001 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X268.307949 Y263.485861 Z6 E9375.076821 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X268.307958 Y263.485854 Z6 E9375.076872 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X269.400191 Y262.495911 Z5.262957 E9382.614021 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X269.400567 Y262.49557 Z5.263211 E9382.616614 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X269.400569 Y262.495569 Z5.26321 E9382.616625 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X269.40057 Y262.495567 Z5.263211 E9382.616636 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X269.400911 Y262.495191 Z5.262957 E9382.619229 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X269.634127 Y262.237877 Z5.436594 E9384.394871 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X270.390854 Y261.402958 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X270.390861 Y261.402949 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X270.605815 Y261.165784 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X271.674916 Y259.724268 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
G1 X272.510531 Y258.330129 Z6 F1800 ; clayline kind=print page=0 layer=0 stroke=stroke-0017 matz0=4 matz1=4 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=0 id=stroke-0017
; CLAYLINE_MARKER page=0 layer=1 text=layer 1 page_id=page-1-rosette-1 page_name=rosette z_mode=calibrated
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0017
G0 X272.510531 Y258.330129 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0017 note=stroke start
G1 X271.739377 Y259.616722 Z6 E9384.706685 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X271.674916 Y259.724268 Z6 E9384.760993 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X270.856059 Y260.828369 Z6 E9385.642127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X270.605815 Y261.165784 Z6 E9386.015884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X269.880588 Y261.965949 Z6 E9387.201195 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X269.551394 Y262.329159 Z6 E9387.845893 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X269.55139 Y262.329163 Z6.000003 E9387.845902 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X269.551386 Y262.329167 Z6 E9387.845911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X269.400569 Y262.495569 Z6 E9388.16352 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X269.234167 Y262.646386 Z6 E9388.495108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X269.234163 Y262.64639 Z6.000003 E9388.495117 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X269.234159 Y262.646394 Z6 E9388.495127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X268.818764 Y263.022886 Z6 E9389.383892 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X268.070784 Y263.700815 Z6 E9391.203899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X267.6768 Y263.993014 Z6 E9392.190216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X266.629268 Y264.769916 Z6 E9395.137018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X266.461312 Y264.870585 Z6 E9395.620167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X265.174719 Y265.641739 Z6 E9399.673746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X265.089904 Y265.692576 Z6 E9399.96288 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X263.82331 Y266.29163 Z6 E9404.350952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X263.467515 Y266.459909 Z6 E9405.681484 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X262.996139 Y266.62857 Z6 E9407.435972 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X262.996081 Y266.628591 Z6.000031 E9407.436218 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X262.996023 Y266.628611 Z6 E9407.436465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X262.425788 Y266.832644 Z6 E9409.651787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X261.777726 Y267.064525 Z6 E9412.292888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X260.990349 Y267.261753 Z6 E9415.576248 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X260.036812 Y267.500601 Z6 E9419.663073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X259.336834 Y267.604433 Z6 E9422.605083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X259.336726 Y267.604449 Z6.000055 E9422.605593 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X258.2616 Y267.763929 Z5.895375 E9427.145264 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=5.895375 note=collision lift
G1 X258.261537 Y267.763938 Z5.895407 E9427.14556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.895375 matz1=5.895407 note=collision lift
G1 X257.554964 Y267.79865 Z5.827274 E9430.100303 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.895407 matz1=5.827274 note=collision lift
G1 X257.554644 Y267.798666 Z5.827434 E9430.101793 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.827274 matz1=5.827434 note=collision lift
G1 X256.469197 Y267.85199 Z5.284057 E9435.1533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.827434 matz1=5.284057 note=collision lift
G1 X256.469 Y267.852 Z5.284155 E9435.154216 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.284057 matz1=5.284155 note=collision lift
G1 X255.762106 Y267.817273 Z4.930285 E9438.443989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.284155 matz1=4.930285 note=collision lift
G1 X254.676463 Y267.763938 Z4.386808 E9443.496414 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=4.930285 matz1=4.386808 note=collision lift
G1 X253.91122 Y267.650425 Z4 E9447.092372 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=4.386808 matz1=4 note=collision lift
G1 X252.901188 Y267.500601 Z4 E9451.337541 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X251.160274 Y267.064525 Z4 E9458.799034 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X249.470485 Y266.459909 Z4 E9466.260526 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X247.848096 Y265.692576 Z4 E9473.722019 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X246.308732 Y264.769916 Z4 E9481.183511 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X244.867216 Y263.700815 Z4 E9488.645004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X243.537431 Y262.495569 Z4 E9496.106496 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X242.332185 Y261.165784 Z4 E9503.567989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X241.263084 Y259.724268 Z4 E9511.029481 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X240.340424 Y258.184904 Z4 E9518.490973 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X239.573091 Y256.562515 Z4 E9525.952466 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X238.968475 Y254.872726 Z4 E9533.413958 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X238.532399 Y253.131812 Z4 E9540.875451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X238.269062 Y251.356537 Z4 E9548.336943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X238.181 Y249.564 Z4 E9555.798436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X238.269062 Y247.771463 Z4 E9563.259928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X238.532399 Y245.996188 Z4 E9570.721421 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X238.968475 Y244.255274 Z4 E9578.182913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X239.573091 Y242.565485 Z4 E9585.644406 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X240.340424 Y240.943096 Z4 E9593.105898 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X241.263084 Y239.403732 Z4 E9600.56739 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X242.332185 Y237.962216 Z4 E9608.028883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X243.537431 Y236.632431 Z4 E9615.490375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X244.867216 Y235.427185 Z4 E9622.951868 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X246.308732 Y234.358084 Z4 E9630.41336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X247.848096 Y233.435424 Z4 E9637.874853 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X249.470485 Y232.668091 Z4 E9645.336345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X251.160274 Y232.063475 Z4 E9652.797838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X252.901188 Y231.627399 Z4 E9660.25933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X254.676463 Y231.364062 Z4 E9667.720823 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X256.469 Y231.276 Z4 E9675.182315 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X258.261537 Y231.364062 Z4 E9682.643807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X260.036812 Y231.627399 Z4 E9690.1053 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X261.777726 Y232.063475 Z4 E9697.566792 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X263.467515 Y232.668091 Z4 E9705.028285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X265.089904 Y233.435424 Z4 E9712.489777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X266.629268 Y234.358084 Z4 E9719.95127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X268.070784 Y235.427185 Z4 E9727.412762 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X269.400569 Y236.632431 Z4 E9734.874255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X270.605815 Y237.962216 Z4 E9742.335747 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X271.674916 Y239.403732 Z4 E9749.79724 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X272.597576 Y240.943096 Z4 E9757.258732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X273.364909 Y242.565485 Z4 E9764.720224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X273.969525 Y244.255274 Z4 E9772.181717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X274.405601 Y245.996188 Z4 E9779.643209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X274.555518 Y247.006843 Z4 E9783.891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017
G1 X274.668938 Y247.771463 Z4.386493 E9787.484028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=4 matz1=4.386493 note=collision lift
G1 X274.722273 Y248.857106 Z4.929969 E9792.536453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=4.386493 matz1=4.929969 note=collision lift
G1 X274.757 Y249.564 Z5.28384 E9795.826225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=4.929969 matz1=5.28384 note=collision lift
G1 X274.75699 Y249.564197 Z5.283741 E9795.827142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.28384 matz1=5.283741 note=collision lift
G1 X274.703666 Y250.649644 Z5.827119 E9800.878649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.283741 matz1=5.827119 note=collision lift
G1 X274.70365 Y250.649964 Z5.826959 E9800.880137 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.827119 matz1=5.826959 note=collision lift
G1 X274.668938 Y251.356537 Z5.895216 E9803.834931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.826959 matz1=5.895216 note=collision lift
G1 X274.668929 Y251.356601 Z5.895184 E9803.835228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.895216 matz1=5.895184 note=collision lift
G1 X274.509449 Y252.431726 Z6.000055 E9808.374974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=5.895184 matz1=6 note=collision lift
G1 X274.509433 Y252.431835 Z6 E9808.375485 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X274.405601 Y253.131812 Z6 E9811.317494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X274.271133 Y253.668639 Z6 E9813.618313 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X273.969525 Y254.872726 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X273.364909 Y256.562515 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X272.597576 Y258.184904 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
G1 X272.510531 Y258.330129 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0017 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0017
G0 X272.510531 Y258.330129 Z12 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0016 note=intra-page lift
G0 X272.717295 Y258.454058 Z12 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0016 note=intra-page XY
G0 X272.717295 Y258.454058 Z8 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0016 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0016
G1 X271.823746 Y259.658869 Z8 E9813.930127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X271.158189 Y260.556269 Z8 E9814.567627 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X270.901163 Y260.839853 Z8 E9814.865568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X269.893824 Y261.95128 Z8 E9816.424637 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X269.400538 Y262.495538 Z8 E9817.415568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X268.833369 Y263.00959 Z8 E9818.607333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X267.721942 Y264.016928 Z8 E9821.413657 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X267.461269 Y264.253189 Z8 E9822.162136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X266.539033 Y264.937165 Z8 E9824.843609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X265.359058 Y265.812295 Z8 E9828.807332 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X265.332536 Y265.828191 Z8 E9828.897188 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X264.045943 Y266.599345 Z8 E9833.574394 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X263.114151 Y267.15784 Z8 E9837.351155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X262.740215 Y267.334699 Z8 E9838.875228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X261.384231 Y267.976031 Z8 E9844.79969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X260.748167 Y268.276867 Z8 E9847.724995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X259.167166 Y268.842558 Z8 E9854.706122 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X259.166485 Y268.842802 Z8 E9854.70913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X259.04712 Y268.885512 Z7.978896 E9855.243457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X259.045758 Y268.885999 Z7.979619 E9855.250179 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X258.925031 Y268.929196 Z7.95062 E9855.79673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X258.283892 Y269.158599 Z7.610148 E9858.961923 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X255.745059 Y269.794543 Z6.301513 E9871.127635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X253.156117 Y270.178577 Z4.992878 E9883.293346 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=4.992878 note=collision lift
G1 X251.172753 Y270.276013 Z4 E9892.523628 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.992878 matz1=4 note=collision lift
G1 X250.542 Y270.307 Z4 E9895.149156 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X247.927883 Y270.178577 Z4 E9906.0305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X245.338941 Y269.794543 Z4 E9916.911843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X242.800108 Y269.158599 Z4 E9927.793186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X240.335833 Y268.276867 Z4 E9938.674529 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X237.969849 Y267.15784 Z4 E9949.555872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X235.724942 Y265.812295 Z4 E9960.437215 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X233.622731 Y264.253189 Z4 E9971.318558 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X231.683462 Y262.495538 Z4 E9982.199902 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X229.925811 Y260.556269 Z4 E9993.081245 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X228.366705 Y258.454058 Z4 E10003.962588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X227.02116 Y256.209151 Z4 E10014.843931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X225.902133 Y253.843167 Z4 E10025.725274 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X225.020401 Y251.378892 Z4 E10036.606617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X224.384457 Y248.840059 Z4 E10047.487961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X224.000423 Y246.251117 Z4 E10058.369304 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X223.872 Y243.637 Z4 E10069.250647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X224.000423 Y241.022883 Z4 E10080.13199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X224.384457 Y238.433941 Z4 E10091.013333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X225.020401 Y235.895108 Z4 E10101.894676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X225.902133 Y233.430833 Z4 E10112.77602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X227.02116 Y231.064849 Z4 E10123.657363 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X228.366705 Y228.819942 Z4 E10134.538706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X229.925811 Y226.717731 Z4 E10145.420049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X231.683462 Y224.778462 Z4 E10156.301392 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X233.622731 Y223.020811 Z4 E10167.182735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X235.724942 Y221.461705 Z4 E10178.064079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X237.969849 Y220.11616 Z4 E10188.945422 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X240.335833 Y218.997133 Z4 E10199.826765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X242.800108 Y218.115401 Z4 E10210.708108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X245.338941 Y217.479457 Z4 E10221.589451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X247.927883 Y217.095423 Z4 E10232.470794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X250.542 Y216.967 Z4 E10243.352138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X253.156117 Y217.095423 Z4 E10254.233481 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X255.745059 Y217.479457 Z4 E10265.114824 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X258.283892 Y218.115401 Z4 E10275.996167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X260.748167 Y218.997133 Z4 E10286.87751 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X263.114151 Y220.11616 Z4 E10297.758853 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X265.359058 Y221.461705 Z4 E10308.640196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X267.461269 Y223.020811 Z4 E10319.52154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X269.400538 Y224.778462 Z4 E10330.402883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X271.158189 Y226.717731 Z4 E10341.284226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X272.717295 Y228.819942 Z4 E10352.165569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X274.06284 Y231.064849 Z4 E10363.046912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X275.181867 Y233.430833 Z4 E10373.928255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X276.063599 Y235.895108 Z4 E10384.809599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X276.699543 Y238.433941 Z4 E10395.690942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X277.083577 Y241.022883 Z4 E10406.572285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X277.212 Y243.637 Z4 E10417.453628 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X277.181004 Y244.267933 Z4 E10420.079906 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016
G1 X277.083577 Y246.251117 Z4.992788 E10429.30935 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4 matz1=4.992788 note=collision lift
G1 X276.699543 Y248.840059 Z6.301423 E10441.475061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=4.992788 matz1=6 note=collision lift
G1 X276.063599 Y251.378892 Z7.610058 E10453.640773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X275.834196 Y252.020031 Z7.95053 E10456.805966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X275.790999 Y252.140758 Z7.979582 E10457.352565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X275.790511 Y252.142121 Z7.978858 E10457.359297 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X275.747802 Y252.261485 Z8 E10457.893642 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X275.747558 Y252.262167 Z8 E10457.896655 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X275.181867 Y253.843167 Z8 E10464.877776 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X275.081589 Y254.055188 Z8 E10465.852878 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X274.06284 Y256.209151 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
G1 X272.717295 Y258.454058 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0016 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0016
G0 X272.717295 Y258.454058 Z12 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0015 note=intra-page lift
G0 X284.26798 Y266.162765 Z12 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0015 note=intra-page XY
G0 X284.26798 Y266.162765 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0015 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0015
G1 X284.415006 Y267.655542 Z6 E10466.164692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X284.451 Y268.021 Z6 E10466.336056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X284.339969 Y269.148319 Z6 E10467.100133 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X284.26798 Y269.879235 Z6 E10467.785589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X284.045753 Y270.611818 Z6 E10468.659202 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X283.725953 Y271.66606 Z6 E10470.201477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X283.538186 Y272.017347 Z6 E10470.841899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X283.424691 Y272.229681 Z6 E10471.250322 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X283.42333 Y272.232226 Z6.001443 E10471.255905 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X282.893756 Y273.22299 Z5.439749 E10473.648222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=5.439629 note=collision lift
G1 X282.845808 Y273.312694 Z5.388892 E10473.886412 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.439629 matz1=5.388892 note=collision lift
G1 X282.845748 Y273.312806 Z5.388956 E10473.886712 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.388892 matz1=5.388956 note=collision lift
G1 X282.438487 Y273.809056 Z5.068003 E10475.472739 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.388956 matz1=5.068003 note=collision lift
G1 X282.05922 Y274.271194 Z4.769082 E10477.078174 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.068003 matz1=4.769082 note=collision lift
G1 X281.661192 Y274.756192 Z4.455375 E10478.896192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.769082 matz1=4.455375 note=collision lift
G1 X281.109088 Y275.209292 Z4.812487 E10481.131753 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.455375 matz1=4.812487 note=collision lift
G1 X280.714056 Y275.533487 Z5.068003 E10482.83977 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.812487 matz1=5.068003 note=collision lift
G1 X280.217806 Y275.940748 Z5.388956 E10485.1136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.068003 matz1=5.388956 note=collision lift
G1 X280.217694 Y275.940808 Z5.388892 E10485.114065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.388956 matz1=5.388892 note=collision lift
G1 X280.051429 Y276.029679 Z5.483153 E10485.808959 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.388892 matz1=5.482931 note=collision lift
G1 X279.137226 Y276.51833 Z6.001443 E10489.849792 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.482931 matz1=6 note=collision lift
G1 X279.134681 Y276.519691 Z6 E10489.861564 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X278.83675 Y276.678938 Z6 E10491.109793 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X278.57106 Y276.820953 Z6 E10492.249625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X277.42394 Y277.168928 Z6 E10497.034255 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X276.784235 Y277.36298 Z6 E10499.81351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X274.926 Y277.546 Z6 E10507.576535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X273.067765 Y277.36298 Z6 E10515.339561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X272.4562 Y277.177464 Z6 E10517.99656 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X272.453438 Y277.176626 Z6.001443 E10518.009977 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X271.281062 Y276.82099 Z5.388892 E10523.704654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=5.388892 note=collision lift
G1 X271.28094 Y276.820953 Z5.388956 E10523.705246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.388892 matz1=5.388956 note=collision lift
G1 X270.714774 Y276.51833 Z5.068003 E10526.689219 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.388956 matz1=5.068003 note=collision lift
G1 X269.634194 Y275.940748 Z4.455375 E10532.384514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.068003 matz1=4.455375 note=collision lift
G1 X269.137944 Y275.533487 Z4.13439 E10535.368546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.455375 matz1=4.13439 note=collision lift
G1 X268.930175 Y275.362975 Z4 E10536.617898 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.13439 matz1=4 note=collision lift
G1 X268.190808 Y274.756192 Z4 E10540.59447 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X268.001681 Y274.525741 Z4 E10541.833916 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X267.006252 Y273.312806 Z4.784552 E10549.1275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4 matz1=4.784552 note=collision lift
G1 X266.126047 Y271.66606 Z5.718166 E10557.806826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.784552 matz1=5.718166 note=collision lift
G1 X265.58402 Y269.879235 Z6.651779 E10566.486153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.718166 matz1=6 note=collision lift
G1 X265.401 Y268.021 Z7.585392 E10575.16548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X265.482277 Y267.195777 Z8 E10579.019877 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X265.58402 Y266.162765 Z8 E10583.335425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X266.126047 Y264.37594 Z8 E10591.098451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X266.824823 Y263.068623 Z8 E10597.261354 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X267.006252 Y262.729194 Z7.807563 E10599.050345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X268.190808 Y261.285808 Z6.873949 E10607.729672 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X269.634194 Y260.101252 Z7.807563 E10616.408999 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X269.973623 Y259.919823 Z8 E10618.19799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X271.28094 Y259.221047 Z8 E10624.360893 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X273.067765 Y258.67902 Z8 E10632.123919 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X274.100777 Y258.577277 Z8 E10636.439467 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X274.926 Y258.496 Z7.585392 E10640.293865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X276.784235 Y258.67902 Z6.651779 E10648.973191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X278.57106 Y259.221047 Z5.718166 E10657.652518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=5.718166 note=collision lift
G1 X280.217806 Y260.101252 Z4.784552 E10666.331845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.718166 matz1=4.784552 note=collision lift
G1 X281.430741 Y261.096681 Z4 E10673.625428 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.784552 matz1=4 note=collision lift
G1 X281.465272 Y261.125021 Z4 E10673.811149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015
G1 X281.661192 Y261.285808 Z4.126725 E10674.98925 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4 matz1=4.126725 note=collision lift
G1 X282.267975 Y262.025175 Z4.604964 E10679.435192 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.126725 matz1=4.604964 note=collision lift
G1 X282.774018 Y262.64179 Z5.402644 E10684.125244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=4.604964 matz1=5.402644 note=collision lift
G1 X282.845748 Y262.729194 Z5.515713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.402644 matz1=5.515713 note=collision lift
G1 X283.42333 Y263.809774 Z6.74097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=5.515713 matz1=6 note=collision lift
G1 X283.725953 Y264.37594 Z7.382908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X283.72599 Y264.376062 Z7.382908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X283.905124 Y264.966589 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X284.081626 Y265.548438 Z7.999993 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X284.082464 Y265.5512 Z7.997107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
G1 X284.26798 Y266.162765 Z7.677565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0015 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0015
G0 X284.26798 Y266.162765 Z11.677565 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0014 note=intra-page lift
G0 X318.634185 Y256.549008 Z11.677565 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0014 note=intra-page XY
G0 X318.634185 Y256.549008 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0014 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0014
G1 X317.740636 Y257.753819 Z4 E10684.437058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X317.275536 Y258.380934 Z4 E10684.846141 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X316.792526 Y258.913853 Z4 E10685.372499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X315.785188 Y260.02528 Z4 E10686.931568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X315.743869 Y260.070869 Z4 E10687.008833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X314.678031 Y261.036888 Z4 E10689.114265 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X314.053934 Y261.602536 Z4 E10690.613319 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X313.781836 Y261.804338 Z4 E10691.271678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=prime ramp
G1 X313.780689 Y261.805189 Z4.000714 E10691.274856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4 matz1=4.000714 note=collision lift
G1 X313.552673 Y261.974297 Z4.142561 E10691.920588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.000714 matz1=4.142561 note=collision lift
G1 X313.163467 Y262.262951 Z4.384684 E10693.087291 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.142561 matz1=4.384684 note=collision lift
G1 X312.475005 Y262.773549 Z4.813254 E10695.35054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.384684 matz1=4.813254 note=collision lift
G1 X312.222008 Y262.961185 Z4.970746 E10696.246201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.813254 matz1=4.970746 note=collision lift
G1 X311.341414 Y263.488993 Z5.484073 E10699.404119 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.970746 matz1=5.483563 note=collision lift
G1 X310.454606 Y264.020525 Z6.001022 E10702.953374 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.483563 matz1=6 note=collision lift
G1 X310.452853 Y264.021576 Z6 E10702.960757 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X310.265732 Y264.133732 Z6 E10703.672289 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X310.153982 Y264.186585 Z6 E10704.081325 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X308.797999 Y264.827918 Z6 E10709.382159 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X308.203946 Y265.108884 Z6 E10711.900891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X307.410361 Y265.392833 Z6 E10715.306621 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X306.056506 Y265.87725 Z6 E10721.284754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X304.766965 Y266.200264 Z6 E10726.81168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X304.766457 Y266.200391 Z6.00017 E10726.813966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X304.766127 Y266.200474 Z6 E10726.815551 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X303.844094 Y266.431431 Z6 E10730.767347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X301.588016 Y266.766088 Z6 E10740.249661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X301.368813 Y266.776857 Z6 E10741.162101 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X301.368078 Y266.776893 Z6.000368 E10741.165522 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X301.366037 Y266.776993 Z6 E10741.174155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X300.917803 Y266.799014 Z6 E10743.039943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X300.665625 Y266.811402 Z5.873759 E10744.21354 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=5.873759 note=collision lift
G1 X299.31 Y266.878 Z5.629424 E10749.947078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.873759 matz1=5.629424 note=collision lift
G1 X299.3089 Y266.877946 Z5.628873 E10749.952199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.629424 matz1=5.628873 note=collision lift
G1 X299.091538 Y266.867268 Z5.589696 E10750.871518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.628873 matz1=5.589696 note=collision lift
G1 X299.090062 Y266.867195 Z5.590435 E10750.878388 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.589696 matz1=5.590435 note=collision lift
G1 X297.910637 Y266.809254 Z5.000013 E10756.367252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.590435 matz1=5.000013 note=collision lift
G1 X297.609535 Y266.794462 Z5.150746 E10757.768533 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.000013 matz1=5.150746 note=collision lift
G1 X297.5836 Y266.793187 Z5.158798 E10757.88156 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.150746 matz1=5.158798 note=collision lift
G1 X297.578943 Y266.792959 Z5.16113 E10757.903235 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.158798 matz1=5.16113 note=collision lift
G1 X297.520724 Y266.790099 Z5.165528 E10758.146262 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.16113 matz1=5.165528 note=collision lift
G1 X297.517758 Y266.789953 Z5.167013 E10758.160065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.165528 matz1=5.167013 note=collision lift
G1 X297.398454 Y266.784092 Z5.155961 E10758.658791 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.167013 matz1=5.155961 note=collision lift
G1 X297.395388 Y266.783941 Z5.157496 E10758.67306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.155961 matz1=5.157496 note=collision lift
G1 X297.149774 Y266.771875 Z5.105225 E10759.71828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.157496 matz1=5.105225 note=collision lift
G1 X297.143132 Y266.771549 Z5.1019 E10759.749188 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.105225 matz1=5.1019 note=collision lift
G1 X297.035922 Y266.766282 Z5.081913 E10760.203125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.1019 matz1=5.081913 note=collision lift
G1 X297.031984 Y266.766088 Z5.083885 E10760.221454 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.081913 matz1=5.083885 note=collision lift
G1 X296.845952 Y266.738493 Z5.064779 E10761.00737 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.083885 matz1=5.064779 note=collision lift
G1 X294.993726 Y266.463741 Z6.001022 E10769.71117 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.064779 matz1=6 note=collision lift
G1 X294.991704 Y266.463441 Z6 E10769.72067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X294.775906 Y266.431431 Z6 E10770.627673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X292.563494 Y265.87725 Z6 E10780.109986 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X290.416054 Y265.108884 Z6 E10789.5923 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X288.354268 Y264.133732 Z6 E10799.074613 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X288.167147 Y264.021576 Z6 E10799.981616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X288.165394 Y264.020525 Z6.001022 E10799.991116 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X286.397992 Y262.961185 Z4.970746 E10809.569097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=4.970746 note=collision lift
G1 X285.456533 Y262.262951 Z4.384684 E10815.01742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.970746 matz1=4.384684 note=collision lift
G1 X284.839311 Y261.805189 Z4.000714 E10818.588874 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.384684 matz1=4.000714 note=collision lift
G1 X284.838164 Y261.804338 Z4 E10818.595512 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.000714 matz1=4 note=collision lift
G1 X284.566066 Y261.602536 Z4 E10820.003933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X282.876131 Y260.070869 Z4 E10829.486246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X281.344464 Y258.380934 Z4 E10838.968559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X281.228583 Y258.224687 Z4 E10839.777316 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X279.985815 Y256.549008 Z5.043117 E10849.474647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4 matz1=5.043117 note=collision lift
G1 X278.813268 Y254.592732 Z6.183499 E10860.076196 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=5.043117 matz1=6 note=collision lift
G1 X277.838116 Y252.530946 Z7.323881 E10870.677744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X277.382561 Y251.257754 Z8 E10876.963277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X277.06975 Y250.383506 Z8 E10880.823639 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.515569 Y248.171094 Z8 E10890.305952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.434347 Y247.623537 Z8 E10892.607341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.433625 Y247.618671 Z8 E10892.62779 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.322732 Y246.871089 Z7.682579 E10896.035767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.322603 Y246.87022 Z7.683019 E10896.039852 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.211581 Y246.121769 Z7.338042 E10899.497133 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.180912 Y245.915016 Z7.233534 E10900.468685 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.180728 Y245.911268 Z7.231658 E10900.486127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.156323 Y245.414508 Z6.995331 E10902.775468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.156246 Y245.41293 Z6.996121 E10902.782812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.069 Y243.637 Z6.107085 E10911.047726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=6 note=collision lift
G1 X276.180912 Y241.358984 Z4.966704 E10921.649275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=6 matz1=4.966704 note=collision lift
G1 X276.464602 Y239.446503 Z4 E10930.636225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.966704 matz1=4 note=collision lift
G1 X276.515569 Y239.102906 Z4 E10932.080366 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X277.06975 Y236.890494 Z4 E10941.562679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X277.838116 Y234.743054 Z4 E10951.044992 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X278.813268 Y232.681268 Z4 E10960.527306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X279.985815 Y230.724992 Z4 E10970.009619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X281.344464 Y228.893066 Z4 E10979.491932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X282.876131 Y227.203131 Z4 E10988.974246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X284.566066 Y225.671464 Z4 E10998.456559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X286.397992 Y224.312815 Z4 E11007.938872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X288.354268 Y223.140268 Z4 E11017.421186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X290.416054 Y222.165116 Z4 E11026.903499 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X292.563494 Y221.39675 Z4 E11036.385812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X294.775906 Y220.842569 Z4 E11045.868126 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X297.031984 Y220.507912 Z4 E11055.350439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X299.31 Y220.396 Z4 E11064.832752 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X301.588016 Y220.507912 Z4 E11074.315066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X303.844094 Y220.842569 Z4 E11083.797379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X306.056506 Y221.39675 Z4 E11093.279692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X308.203946 Y222.165116 Z4 E11102.762006 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X310.265732 Y223.140268 Z4 E11112.244319 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X312.222008 Y224.312815 Z4 E11121.726632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X314.053934 Y225.671464 Z4 E11131.208946 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X315.743869 Y227.203131 Z4 E11140.691259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X317.275536 Y228.893066 Z4 E11150.173572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X318.634185 Y230.724992 Z4 E11159.655886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X319.806732 Y232.681268 Z4 E11169.138199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X320.781884 Y234.743054 Z4 E11178.620512 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X321.55025 Y236.890494 Z4 E11188.102825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X322.104431 Y239.102906 Z4 E11197.585139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X322.439088 Y241.358984 Z4 E11207.067452 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X322.551 Y243.637 Z4 E11216.549765 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X322.439088 Y245.915016 Z4 E11226.032079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X322.181411 Y247.652137 Z4 E11233.333211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X322.18141 Y247.652144 Z4.000004 E11233.333245 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4 matz1=4.000004 note=collision lift
G1 X322.172033 Y247.715354 Z4.028636 E11233.624368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.000004 matz1=4.028636 note=collision lift
G1 X322.170783 Y247.723782 Z4.032896 E11233.66397 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.028636 matz1=4.032896 note=collision lift
G1 X322.111742 Y248.121805 Z4.195959 E11235.469009 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.032896 matz1=4.195959 note=collision lift
G1 X322.104431 Y248.171094 Z4.220873 E11235.700626 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.195959 matz1=4.220873 note=collision lift
G1 X321.87995 Y249.067272 Z4.520159 E11239.738125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.220873 matz1=4.520159 note=collision lift
G1 X321.879256 Y249.070042 Z4.518731 E11239.751402 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.520159 matz1=4.518731 note=collision lift
G1 X321.729269 Y249.668823 Z4.686429 E11242.410774 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.518731 matz1=4.686429 note=collision lift
G1 X321.728471 Y249.67201 Z4.684786 E11242.426045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.686429 matz1=4.684786 note=collision lift
G1 X321.640919 Y250.021535 Z4.762246 E11243.95832 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.684786 matz1=4.762246 note=collision lift
G1 X321.63976 Y250.026165 Z4.764632 E11243.980504 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.762246 matz1=4.764632 note=collision lift
G1 X321.55025 Y250.383506 Z4.816536 E11245.527183 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.764632 matz1=4.816536 note=collision lift
G1 X321.549584 Y250.385369 Z4.815547 E11245.536377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.816536 matz1=4.815547 note=collision lift
G1 X321.484302 Y250.567819 Z4.785604 E11246.351572 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.815547 matz1=4.785604 note=collision lift
G1 X321.469553 Y250.609039 Z4.763714 E11246.555071 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.785604 matz1=4.763714 note=collision lift
G1 X321.451328 Y250.659975 Z4.740707 E11246.79948 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.763714 matz1=4.740707 note=collision lift
G1 X320.952255 Y252.054791 Z4 E11253.685453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 matz0=4.740707 matz1=4 note=collision lift
G1 X320.929601 Y252.118104 Z4 E11253.965021 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014
G1 X320.781884 Y252.530946 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X319.806732 Y254.592732 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
G1 X318.634185 Y256.549008 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0014 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0014
G0 X318.634185 Y256.549008 Z10 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0013 note=intra-page lift
G0 X333.384871 Y265.605531 Z10 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0013 note=intra-page XY
G0 X333.384871 Y265.605531 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0013 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0013
G1 X332.098278 Y264.834377 Z6 E11254.276835 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X331.990732 Y264.769916 Z6 E11254.331143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X330.886631 Y263.951059 Z6 E11255.212276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X330.549216 Y263.700815 Z6 E11255.586034 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X329.749051 Y262.975588 Z6 E11256.771345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X329.385841 Y262.646394 Z6 E11257.416043 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X329.385837 Y262.64639 Z6.000003 E11257.416052 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X329.385833 Y262.646386 Z6 E11257.416061 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X329.219431 Y262.495569 Z6 E11257.733669 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X329.068614 Y262.329167 Z6 E11258.065257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X329.06861 Y262.329163 Z6.000003 E11258.065267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X329.068606 Y262.329159 Z6 E11258.065276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X328.692114 Y261.913764 Z6 E11258.954042 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X328.014185 Y261.165784 Z6 E11260.774049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X327.721986 Y260.7718 Z6 E11261.760365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X326.945084 Y259.724268 Z6 E11264.707168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X326.844415 Y259.556312 Z6 E11265.190317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X326.073261 Y258.269719 Z6 E11269.243896 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X326.022424 Y258.184904 Z6 E11269.53303 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X325.42337 Y256.91831 Z6 E11273.921102 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X325.255091 Y256.562515 Z6 E11275.251634 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X325.08643 Y256.091139 Z6 E11277.006121 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X325.086409 Y256.091081 Z6.000031 E11277.006368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X325.086389 Y256.091023 Z6 E11277.006615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X324.882356 Y255.520788 Z6 E11279.221936 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X324.650475 Y254.872726 Z6 E11281.863038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X324.453247 Y254.085349 Z6 E11285.146398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X324.214399 Y253.131812 Z6 E11289.233223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X324.110567 Y252.431834 Z6 E11292.175233 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X324.110551 Y252.431726 Z6.000055 E11292.175743 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X323.951071 Y251.3566 Z5.895375 E11296.715413 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=5.895375 note=collision lift
G1 X323.951062 Y251.356537 Z5.895407 E11296.71571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.895375 matz1=5.895407 note=collision lift
G1 X323.91635 Y250.649964 Z5.827274 E11299.670453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.895407 matz1=5.827274 note=collision lift
G1 X323.916334 Y250.649644 Z5.827434 E11299.671942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.827274 matz1=5.827434 note=collision lift
G1 X323.86301 Y249.564197 Z5.284057 E11304.723449 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.827434 matz1=5.284057 note=collision lift
G1 X323.863 Y249.564 Z5.284155 E11304.724366 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.284057 matz1=5.284155 note=collision lift
G1 X323.897727 Y248.857106 Z4.930285 E11308.014138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.284155 matz1=4.930285 note=collision lift
G1 X323.951062 Y247.771463 Z4.386808 E11313.066563 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=4.930285 matz1=4.386808 note=collision lift
G1 X324.064575 Y247.00622 Z4 E11316.662521 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=4.386808 matz1=4 note=collision lift
G1 X324.214399 Y245.996188 Z4 E11320.907691 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X324.650475 Y244.255274 Z4 E11328.369184 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X325.255091 Y242.565485 Z4 E11335.830676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X326.022424 Y240.943096 Z4 E11343.292169 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X326.945084 Y239.403732 Z4 E11350.753661 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X328.014185 Y237.962216 Z4 E11358.215153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X329.219431 Y236.632431 Z4 E11365.676646 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X330.549216 Y235.427185 Z4 E11373.138138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X331.990732 Y234.358084 Z4 E11380.599631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X333.530096 Y233.435424 Z4 E11388.061123 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X335.152485 Y232.668091 Z4 E11395.522616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X336.842274 Y232.063475 Z4 E11402.984108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X338.583188 Y231.627399 Z4 E11410.445601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X340.358463 Y231.364062 Z4 E11417.907093 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X342.151 Y231.276 Z4 E11425.368586 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X343.943537 Y231.364062 Z4 E11432.830078 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X345.718812 Y231.627399 Z4 E11440.29157 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X347.459726 Y232.063475 Z4 E11447.753063 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X349.149515 Y232.668091 Z4 E11455.214555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X350.771904 Y233.435424 Z4 E11462.676048 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X352.311268 Y234.358084 Z4 E11470.13754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X353.752784 Y235.427185 Z4 E11477.599033 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X355.082569 Y236.632431 Z4 E11485.060525 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X356.287815 Y237.962216 Z4 E11492.522018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X357.356916 Y239.403732 Z4 E11499.98351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X358.279576 Y240.943096 Z4 E11507.445003 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X359.046909 Y242.565485 Z4 E11514.906495 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X359.651525 Y244.255274 Z4 E11522.367987 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X360.087601 Y245.996188 Z4 E11529.82948 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X360.350938 Y247.771463 Z4 E11537.290972 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X360.439 Y249.564 Z4 E11544.752465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X360.350938 Y251.356537 Z4 E11552.213957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X360.087601 Y253.131812 Z4 E11559.67545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X359.651525 Y254.872726 Z4 E11567.136942 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X359.046909 Y256.562515 Z4 E11574.598435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X358.279576 Y258.184904 Z4 E11582.059927 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X357.356916 Y259.724268 Z4 E11589.52142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X356.287815 Y261.165784 Z4 E11596.982912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X355.082569 Y262.495569 Z4 E11604.444404 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X353.752784 Y263.700815 Z4 E11611.905897 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X352.311268 Y264.769916 Z4 E11619.367389 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X350.771904 Y265.692576 Z4 E11626.828882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X349.149515 Y266.459909 Z4 E11634.290374 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X347.459726 Y267.064525 Z4 E11641.751867 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X345.718812 Y267.500601 Z4 E11649.213359 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X344.708157 Y267.650518 Z4 E11653.46115 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013
G1 X343.943537 Y267.763938 Z4.386493 E11657.054178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=4 matz1=4.386493 note=collision lift
G1 X342.857894 Y267.817273 Z4.929969 E11662.106603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=4.386493 matz1=4.929969 note=collision lift
G1 X342.151 Y267.852 Z5.28384 E11665.396375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=4.929969 matz1=5.28384 note=collision lift
G1 X342.150803 Y267.85199 Z5.283741 E11665.397292 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.28384 matz1=5.283741 note=collision lift
G1 X341.065356 Y267.798666 Z5.827119 E11670.448799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.283741 matz1=5.827119 note=collision lift
G1 X341.065036 Y267.79865 Z5.826959 E11670.450287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.827119 matz1=5.826959 note=collision lift
G1 X340.358463 Y267.763938 Z5.895216 E11673.405081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.826959 matz1=5.895216 note=collision lift
G1 X340.358399 Y267.763929 Z5.895184 E11673.405377 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.895216 matz1=5.895184 note=collision lift
G1 X339.283274 Y267.604449 Z6.000055 E11677.945124 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=5.895184 matz1=6 note=collision lift
G1 X339.283165 Y267.604433 Z6 E11677.945634 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X338.583188 Y267.500601 Z6 E11680.887644 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X338.046361 Y267.366133 Z6 E11683.188463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X336.842274 Y267.064525 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X335.152485 Y266.459909 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X333.530096 Y265.692576 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
G1 X333.384871 Y265.605531 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0013 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0013
G0 X333.384871 Y265.605531 Z12 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0012 note=intra-page lift
G0 X333.260942 Y265.812295 Z12 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0012 note=intra-page XY
G0 X333.260942 Y265.812295 Z8 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0012 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0012
G1 X332.056131 Y264.918746 Z8 E11683.500277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X331.158731 Y264.253189 Z8 E11684.137777 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X330.875147 Y263.996163 Z8 E11684.435718 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X329.76372 Y262.988824 Z8 E11685.994787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X329.219462 Y262.495538 Z8 E11686.985718 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X328.70541 Y261.928369 Z8 E11688.177483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X327.698072 Y260.816942 Z8 E11690.983807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X327.461811 Y260.556269 Z8 E11691.732286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X326.777835 Y259.634033 Z8 E11694.413758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X325.902705 Y258.454058 Z8 E11698.377482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X325.886809 Y258.427536 Z8 E11698.467337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X325.115655 Y257.140943 Z8 E11703.144544 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X324.55716 Y256.209151 Z8 E11706.921305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X324.380301 Y255.835215 Z8 E11708.445378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X323.738969 Y254.479231 Z8 E11714.369839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X323.438133 Y253.843167 Z8 E11717.295145 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.872442 Y252.262166 Z8 E11724.276272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.872198 Y252.261485 Z8 E11724.27928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.829488 Y252.14212 Z7.978896 E11724.813607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.829001 Y252.140758 Z7.979619 E11724.820329 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.785804 Y252.020031 Z7.95062 E11725.36688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.556401 Y251.378892 Z7.610148 E11728.532073 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.170737 Y249.839236 Z6.816536 E11735.909878 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.016805 Y249.224704 Z6.816536 E11738.543736 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X322.016564 Y249.223743 Z6.817032 E11738.548344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.920457 Y248.840059 Z6.76951 E11740.204625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.920262 Y248.838748 Z6.768847 E11740.210784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.915548 Y248.806968 Z6.764634 E11740.3455 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.915539 Y248.806906 Z6.764603 E11740.345793 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.914866 Y248.802369 Z6.762463 E11740.366833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.914797 Y248.801908 Z6.762696 E11740.368998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.860314 Y248.434614 Z6.686429 E11741.944969 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.859432 Y248.428666 Z6.686429 E11741.969967 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.858973 Y248.425571 Z6.687993 E11741.98451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.770375 Y247.828289 Z6.521333 E11744.588759 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.769466 Y247.822164 Z6.524429 E11744.617541 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.648575 Y247.00718 Z6.225815 E11748.260966 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.612673 Y246.765151 Z6.103477 E11749.398286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.590633 Y246.616567 Z6.033638 E11750.086987 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X321.536423 Y246.251117 Z5.848914 E11751.804273 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=5.848914 note=collision lift
G1 X321.408 Y243.637 Z4.540279 E11763.969985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=5.848914 matz1=4.540279 note=collision lift
G1 X321.46102 Y242.557743 Z4 E11768.992686 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=4.540279 matz1=4 note=collision lift
G1 X321.536423 Y241.022883 Z4 E11775.381589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X321.920457 Y238.433941 Z4 E11786.262932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X322.556401 Y235.895108 Z4 E11797.144275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X323.438133 Y233.430833 Z4 E11808.025618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X324.55716 Y231.064849 Z4 E11818.906961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X325.902705 Y228.819942 Z4 E11829.788305 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X327.461811 Y226.717731 Z4 E11840.669648 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X329.219462 Y224.778462 Z4 E11851.550991 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X331.158731 Y223.020811 Z4 E11862.432334 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X333.260942 Y221.461705 Z4 E11873.313677 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X335.505849 Y220.11616 Z4 E11884.19502 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X337.871833 Y218.997133 Z4 E11895.076364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X340.336108 Y218.115401 Z4 E11905.957707 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X342.874941 Y217.479457 Z4 E11916.83905 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X345.463883 Y217.095423 Z4 E11927.720393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X348.078 Y216.967 Z4 E11938.601736 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X350.692117 Y217.095423 Z4 E11949.483079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X353.281059 Y217.479457 Z4 E11960.364423 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X355.819892 Y218.115401 Z4 E11971.245766 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X358.284167 Y218.997133 Z4 E11982.127109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X360.650151 Y220.11616 Z4 E11993.008452 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X362.895058 Y221.461705 Z4 E12003.889795 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X364.997269 Y223.020811 Z4 E12014.771138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X366.936538 Y224.778462 Z4 E12025.652482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X368.694189 Y226.717731 Z4 E12036.533825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X370.253295 Y228.819942 Z4 E12047.415168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X371.59884 Y231.064849 Z4 E12058.296511 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X372.717867 Y233.430833 Z4 E12069.177854 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X373.599599 Y235.895108 Z4 E12080.059197 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X374.235543 Y238.433941 Z4 E12090.94054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X374.619577 Y241.022883 Z4 E12101.821884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X374.748 Y243.637 Z4 E12112.703227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X374.619577 Y246.251117 Z4 E12123.58457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X374.235543 Y248.840059 Z4 E12134.465913 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X373.599599 Y251.378892 Z4 E12145.347256 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X372.717867 Y253.843167 Z4 E12156.228599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X371.59884 Y256.209151 Z4 E12167.109943 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X370.253295 Y258.454058 Z4 E12177.991286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X368.694189 Y260.556269 Z4 E12188.872629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X366.936538 Y262.495538 Z4 E12199.753972 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X364.997269 Y264.253189 Z4 E12210.635315 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X362.895058 Y265.812295 Z4 E12221.516658 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X360.650151 Y267.15784 Z4 E12232.398002 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X358.284167 Y268.276867 Z4 E12243.279345 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X355.819892 Y269.158599 Z4 E12254.160688 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X353.281059 Y269.794543 Z4 E12265.042031 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X350.692117 Y270.178577 Z4 E12275.923374 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X348.078 Y270.307 Z4 E12286.804717 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X347.447067 Y270.276004 Z4 E12289.430995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012
G1 X345.463883 Y270.178577 Z4.992788 E12298.660439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=4 matz1=4.992788 note=collision lift
G1 X342.874941 Y269.794543 Z6.301423 E12310.82615 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=4.992788 matz1=6 note=collision lift
G1 X340.336108 Y269.158599 Z7.610058 E12322.991862 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X339.694969 Y268.929196 Z7.95053 E12326.157055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X339.574242 Y268.885999 Z7.979582 E12326.703654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X339.572879 Y268.885511 Z7.978858 E12326.710386 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X339.453515 Y268.842802 Z8 E12327.244731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X339.452833 Y268.842558 Z8 E12327.247745 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X337.871833 Y268.276867 Z8 E12334.228866 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X337.659812 Y268.176589 Z8 E12335.203968 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X335.505849 Y267.15784 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
G1 X333.260942 Y265.812295 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0012 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0012
G0 X333.260942 Y265.812295 Z12 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0011 note=intra-page lift
G0 X325.552235 Y277.36298 Z12 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0011 note=intra-page XY
G0 X325.552235 Y277.36298 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0011 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0011
G1 X324.059458 Y277.510006 Z6 E12335.515781 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X323.694 Y277.546 Z6 E12335.687145 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X322.566681 Y277.434969 Z6 E12336.451223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X321.835765 Y277.36298 Z6 E12337.136678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X321.103182 Y277.140753 Z6 E12338.010291 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X320.04894 Y276.820953 Z6 E12339.552566 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X319.697653 Y276.633186 Z6 E12340.192988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X319.485319 Y276.519691 Z6 E12340.601411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X319.482774 Y276.51833 Z6.001443 E12340.606995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X318.49201 Y275.988756 Z5.439749 E12342.999312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=5.439629 note=collision lift
G1 X318.402306 Y275.940808 Z5.388892 E12343.237501 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.439629 matz1=5.388892 note=collision lift
G1 X318.402194 Y275.940748 Z5.388956 E12343.237801 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.388892 matz1=5.388956 note=collision lift
G1 X317.905944 Y275.533487 Z5.068003 E12344.823828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.388956 matz1=5.068003 note=collision lift
G1 X317.443806 Y275.15422 Z4.769082 E12346.429263 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.068003 matz1=4.769082 note=collision lift
G1 X316.958808 Y274.756192 Z4.455375 E12348.247282 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.769082 matz1=4.455375 note=collision lift
G1 X316.505708 Y274.204088 Z4.812487 E12350.482842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.455375 matz1=4.812487 note=collision lift
G1 X316.181513 Y273.809056 Z5.068003 E12352.190859 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.812487 matz1=5.068003 note=collision lift
G1 X315.774252 Y273.312806 Z5.388956 E12354.464689 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.068003 matz1=5.388956 note=collision lift
G1 X315.774192 Y273.312694 Z5.388892 E12354.465155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.388956 matz1=5.388892 note=collision lift
G1 X315.685321 Y273.146429 Z5.483153 E12355.160049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.388892 matz1=5.482931 note=collision lift
G1 X315.19667 Y272.232226 Z6.001443 E12359.200881 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.482931 matz1=6 note=collision lift
G1 X315.195309 Y272.229681 Z6 E12359.212653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X315.036062 Y271.93175 Z6 E12360.460883 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X314.894047 Y271.66606 Z6 E12361.600714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X314.546072 Y270.51894 Z6 E12366.385344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X314.35202 Y269.879235 Z6 E12369.164599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X314.169 Y268.021 Z6 E12376.927625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X314.35202 Y266.162765 Z6 E12384.69065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X314.537536 Y265.5512 Z6 E12387.347649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X314.538374 Y265.548438 Z6.001443 E12387.361067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X314.89401 Y264.376062 Z5.388892 E12393.055744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=5.388892 note=collision lift
G1 X314.894047 Y264.37594 Z5.388956 E12393.056335 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.388892 matz1=5.388956 note=collision lift
G1 X315.19667 Y263.809774 Z5.068003 E12396.040309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.388956 matz1=5.068003 note=collision lift
G1 X315.774252 Y262.729194 Z4.455375 E12401.735603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.068003 matz1=4.455375 note=collision lift
G1 X316.181513 Y262.232944 Z4.13439 E12404.719635 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.455375 matz1=4.13439 note=collision lift
G1 X316.352025 Y262.025175 Z4 E12405.968988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.13439 matz1=4 note=collision lift
G1 X316.958808 Y261.285808 Z4 E12409.945559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X317.189259 Y261.096681 Z4 E12411.185005 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X318.402194 Y260.101252 Z4.784552 E12418.478589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4 matz1=4.784552 note=collision lift
G1 X320.04894 Y259.221047 Z5.718166 E12427.157916 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.784552 matz1=5.718166 note=collision lift
G1 X321.835765 Y258.67902 Z6.651779 E12435.837242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.718166 matz1=6 note=collision lift
G1 X323.694 Y258.496 Z7.585392 E12444.516569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X324.519223 Y258.577277 Z8 E12448.370967 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X325.552235 Y258.67902 Z8 E12452.686514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X327.33906 Y259.221047 Z8 E12460.44954 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X328.646377 Y259.919823 Z8 E12466.612444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X328.985806 Y260.101252 Z7.807563 E12468.401435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X330.429192 Y261.285808 Z6.873949 E12477.080761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X331.613748 Y262.729194 Z7.807563 E12485.760088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X331.795177 Y263.068623 Z8 E12487.549079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X332.493953 Y264.37594 Z8 E12493.711983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X333.03598 Y266.162765 Z8 E12501.475008 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X333.137723 Y267.195777 Z8 E12505.790556 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X333.219 Y268.021 Z7.585392 E12509.644954 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X333.03598 Y269.879235 Z6.651779 E12518.324281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X332.493953 Y271.66606 Z5.718166 E12527.003607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=5.718166 note=collision lift
G1 X331.613748 Y273.312806 Z4.784552 E12535.682934 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.718166 matz1=4.784552 note=collision lift
G1 X330.618319 Y274.525741 Z4 E12542.976518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.784552 matz1=4 note=collision lift
G1 X330.589979 Y274.560272 Z4 E12543.162239 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011
G1 X330.429192 Y274.756192 Z4.126725 E12544.340339 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4 matz1=4.126725 note=collision lift
G1 X329.689825 Y275.362975 Z4.604964 E12548.786281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.126725 matz1=4.604964 note=collision lift
G1 X329.07321 Y275.869018 Z5.402644 E12553.476334 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=4.604964 matz1=5.402644 note=collision lift
G1 X328.985806 Y275.940748 Z5.515713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.402644 matz1=5.515713 note=collision lift
G1 X327.905226 Y276.51833 Z6.74097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=5.515713 matz1=6 note=collision lift
G1 X327.33906 Y276.820953 Z7.382908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X327.338938 Y276.82099 Z7.382908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X326.748411 Y277.000124 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X326.166562 Y277.176626 Z7.999993 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X326.1638 Y277.177464 Z7.997107 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
G1 X325.552235 Y277.36298 Z7.677565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0011 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0011
G0 X325.552235 Y277.36298 Z11.677565 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0010 note=intra-page lift
G0 X335.687126 Y318.158794 Z11.677565 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0010 note=intra-page XY
G0 X335.687126 Y318.158794 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0010 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0010
G1 X336.842274 Y317.745475 Z6 E12553.68493 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X337.107222 Y317.679109 Z6 E12553.788147 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X338.562269 Y317.314639 Z6 E12554.723589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X338.583188 Y317.309399 Z6 E12554.741585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X339.282944 Y317.2056 Z6 E12555.40338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X339.283274 Y317.205551 Z6.000179 E12555.403772 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X340.010438 Y317.097686 Z5.768902 E12556.282657 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=5.768844 note=collision lift
G1 X340.358312 Y317.046084 Z5.658259 E12556.761324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.768844 matz1=5.658259 note=collision lift
G1 X340.358463 Y317.046062 Z5.658335 E12556.761554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.658259 matz1=5.658335 note=collision lift
G1 X341.065356 Y317.011334 Z5.435672 E12557.839089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.658335 matz1=5.435672 note=collision lift
G1 X341.413057 Y316.994253 Z5.261612 E12558.465354 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.435672 matz1=5.261612 note=collision lift
G1 X342.150823 Y316.958009 Z4.892284 E12559.933252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.261612 matz1=4.892284 note=collision lift
G1 X342.151 Y316.958 Z4.892372 E12559.933627 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.892284 matz1=4.892372 note=collision lift
G1 X342.753082 Y316.987578 Z4.59097 E12561.271678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.892372 matz1=4.59097 note=collision lift
G1 X342.857894 Y316.992727 Z4.538502 E12561.517473 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.59097 matz1=4.538502 note=collision lift
G1 X343.9336 Y317.045574 Z4 E12564.260654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.538502 matz1=4 note=collision lift
G1 X343.943537 Y317.046062 Z4 E12564.284994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X344.110313 Y317.0708 Z4 E12564.701629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X345.594077 Y317.290896 Z4 E12568.755208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X345.718812 Y317.309399 Z4 E12569.124394 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X347.051538 Y317.643229 Z4 E12573.432415 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X347.459726 Y317.745475 Z4 E12574.856535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X348.475842 Y318.109047 Z4 E12578.733249 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X349.149515 Y318.350091 Z4 E12581.48142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X349.858696 Y318.685509 Z4 E12584.65771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 note=prime ramp
G1 X350.771904 Y319.117424 Z4 E12588.857621 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X352.311268 Y320.040084 Z4 E12596.319114 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X353.752784 Y321.109185 Z4 E12603.780606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X355.082569 Y322.314431 Z4 E12611.242099 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X356.287815 Y323.644216 Z4 E12618.703591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X357.356916 Y325.085732 Z4 E12626.165084 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X358.279576 Y326.625096 Z4 E12633.626576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X359.046909 Y328.247485 Z4 E12641.088069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X359.651525 Y329.937274 Z4 E12648.549561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X360.087601 Y331.678188 Z4 E12656.011054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X360.350938 Y333.453463 Z4 E12663.472546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X360.439 Y335.246 Z4 E12670.934038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X360.350938 Y337.038537 Z4 E12678.395531 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X360.087601 Y338.813812 Z4 E12685.857023 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X359.651525 Y340.554726 Z4 E12693.318516 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X359.046909 Y342.244515 Z4 E12700.780008 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X358.279576 Y343.866904 Z4 E12708.241501 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X357.356916 Y345.406268 Z4 E12715.702993 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X356.287815 Y346.847784 Z4 E12723.164486 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X355.082569 Y348.177569 Z4 E12730.625978 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X353.752784 Y349.382815 Z4 E12738.087471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X352.311268 Y350.451916 Z4 E12745.548963 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X350.771904 Y351.374576 Z4 E12753.010455 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X349.149515 Y352.141909 Z4 E12760.471948 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X347.459726 Y352.746525 Z4 E12767.93344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X345.718812 Y353.182601 Z4 E12775.394933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X343.943537 Y353.445938 Z4 E12782.856425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X342.151 Y353.534 Z4 E12790.317918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X340.358463 Y353.445938 Z4 E12797.77941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X338.583188 Y353.182601 Z4 E12805.240903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X336.842274 Y352.746525 Z4 E12812.702395 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X335.152485 Y352.141909 Z4 E12820.163888 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X333.530096 Y351.374576 Z4 E12827.62538 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X331.990732 Y350.451916 Z4 E12835.086872 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X330.549216 Y349.382815 Z4 E12842.548365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X329.219431 Y348.177569 Z4 E12850.009857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X328.014185 Y346.847784 Z4 E12857.47135 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X326.945084 Y345.406268 Z4 E12864.932842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X326.022424 Y343.866904 Z4 E12872.394335 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X325.255091 Y342.244515 Z4 E12879.855827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X324.650475 Y340.554726 Z4 E12887.31732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X324.214399 Y338.813812 Z4 E12894.778812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X324.064575 Y337.80378 Z4 E12899.023982 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010
G1 X323.951062 Y337.038537 Z4.386808 E12902.61994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4 matz1=4.386808 note=collision lift
G1 X323.897727 Y335.952894 Z4.930285 E12907.672365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.386808 matz1=4.930285 note=collision lift
G1 X323.863 Y335.246 Z5.284155 E12910.962137 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=4.930285 matz1=5.284155 note=collision lift
G1 X323.86301 Y335.245803 Z5.284057 E12910.963054 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.284155 matz1=5.284057 note=collision lift
G1 X323.916334 Y334.160356 Z5.827434 E12916.014561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.284057 matz1=5.827434 note=collision lift
G1 X323.91635 Y334.160036 Z5.827274 E12916.016051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.827434 matz1=5.827274 note=collision lift
G1 X323.951062 Y333.453463 Z5.895407 E12918.970794 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.827274 matz1=5.895407 note=collision lift
G1 X323.951071 Y333.4534 Z5.895375 E12918.97109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.895407 matz1=5.895375 note=collision lift
G1 X324.110551 Y332.378274 Z6.000055 E12923.510761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=5.895375 matz1=6 note=collision lift
G1 X324.110567 Y332.378166 Z6 E12923.51127 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X324.214399 Y331.678188 Z6 E12926.453281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X324.650475 Y329.937274 Z6 E12933.914773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X325.086389 Y328.718977 Z6 E12939.294329 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X325.086409 Y328.718919 Z6.000031 E12939.294616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X325.08643 Y328.718861 Z6 E12939.294903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X325.255091 Y328.247485 Z6 E12941.376326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X326.022424 Y326.625096 Z6 E12948.837819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X326.945084 Y325.085732 Z6 E12956.299311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X328.014185 Y323.644216 Z6 E12963.760804 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X329.068606 Y322.480841 Z6 E12970.288562 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X329.06861 Y322.480837 Z6.000003 E12970.288588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X329.068614 Y322.480833 Z6 E12970.288614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X329.219431 Y322.314431 Z6 E12971.222302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X329.385833 Y322.163614 Z6 E12972.155989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X329.385837 Y322.16361 Z6.000003 E12972.156015 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X329.385841 Y322.163606 Z6 E12972.156041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X330.549216 Y321.109185 Z6 E12978.6838 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X331.313817 Y320.542118 Z6 E12982.641483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X331.990732 Y320.040084 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X333.530096 Y319.117424 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X335.152485 Y318.350091 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X335.623906 Y318.181414 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X335.623919 Y318.181409 Z6.000007 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X335.623932 Y318.181405 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
G1 X335.687126 Y318.158794 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0010 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0010
G0 X335.687126 Y318.158794 Z12 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0009 note=intra-page lift
G0 X335.505849 Y317.65216 Z12 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0009 note=intra-page XY
G0 X335.505849 Y317.65216 Z8 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0009 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0009
G1 X336.861833 Y317.010827 Z8 E12982.953297 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X337.871833 Y316.533133 Z8 E12983.590797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X338.23219 Y316.404195 Z8 E12983.888738 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X339.45232 Y315.967625 Z8 E12985.198994 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X339.453515 Y315.967198 Z8 E12985.200505 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X339.624429 Y315.906044 Z7.909466 E12985.447807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X340.336108 Y315.651401 Z7.532487 E12986.600179 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X340.904699 Y315.508976 Z7.239408 E12987.630503 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X342.206133 Y315.182984 Z6.568588 E12990.436827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X342.874941 Y315.015457 Z6.223853 E12992.12159 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X343.520052 Y314.919763 Z5.897768 E12993.866779 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=5.729694 note=collision lift
G1 X344.847172 Y314.722904 Z5.226947 E12997.920358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=5.729694 matz1=5.173623 note=collision lift
G1 X345.463883 Y314.631423 Z4.915218 E13000.016286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=5.173623 matz1=4.915218 note=collision lift
G1 X346.1812 Y314.596184 Z4.556127 E13002.597564 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=4.915218 matz1=4.556127 note=collision lift
G1 X347.292113 Y314.541608 Z4 E13006.94789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=4.556127 matz1=4 note=collision lift
G1 X347.548267 Y314.529024 Z4 E13007.898398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X348.078 Y314.503 Z4 E13009.921907 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X349.04646 Y314.550577 Z4 E13013.82286 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 note=prime ramp
G1 X350.692117 Y314.631423 Z4 E13020.672957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X353.281059 Y315.015457 Z4 E13031.5543 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X355.819892 Y315.651401 Z4 E13042.435643 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X358.284167 Y316.533133 Z4 E13053.316986 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X360.650151 Y317.65216 Z4 E13064.198329 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X362.895058 Y318.997705 Z4 E13075.079673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X364.997269 Y320.556811 Z4 E13085.961016 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X366.936538 Y322.314462 Z4 E13096.842359 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X368.694189 Y324.253731 Z4 E13107.723702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X370.253295 Y326.355942 Z4 E13118.605045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X371.59884 Y328.600849 Z4 E13129.486388 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X372.717867 Y330.966833 Z4 E13140.367732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X373.599599 Y333.431108 Z4 E13151.249075 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X374.235543 Y335.969941 Z4 E13162.130418 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X374.619577 Y338.558883 Z4 E13173.011761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X374.748 Y341.173 Z4 E13183.893104 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X374.619577 Y343.787117 Z4 E13194.774447 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X374.235543 Y346.376059 Z4 E13205.655791 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X373.599599 Y348.914892 Z4 E13216.537134 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X372.717867 Y351.379167 Z4 E13227.418477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X371.59884 Y353.745151 Z4 E13238.29982 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X370.253295 Y355.990058 Z4 E13249.181163 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X368.694189 Y358.092269 Z4 E13260.062506 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X366.936538 Y360.031538 Z4 E13270.943849 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X364.997269 Y361.789189 Z4 E13281.825193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X362.895058 Y363.348295 Z4 E13292.706536 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X360.650151 Y364.69384 Z4 E13303.587879 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X358.284167 Y365.812867 Z4 E13314.469222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X355.819892 Y366.694599 Z4 E13325.350565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X353.281059 Y367.330543 Z4 E13336.231908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X350.692117 Y367.714577 Z4 E13347.113252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X348.078 Y367.843 Z4 E13357.994595 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X345.463883 Y367.714577 Z4 E13368.875938 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X342.874941 Y367.330543 Z4 E13379.757281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X340.336108 Y366.694599 Z4 E13390.638624 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X337.871833 Y365.812867 Z4 E13401.519967 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X335.505849 Y364.69384 Z4 E13412.401311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X333.260942 Y363.348295 Z4 E13423.282654 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X331.158731 Y361.789189 Z4 E13434.163997 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X329.219462 Y360.031538 Z4 E13445.04534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X327.461811 Y358.092269 Z4 E13455.926683 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X325.902705 Y355.990058 Z4 E13466.808026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X324.55716 Y353.745151 Z4 E13477.68937 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X323.438133 Y351.379167 Z4 E13488.570713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X322.556401 Y348.914892 Z4 E13499.452056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X321.920457 Y346.376059 Z4 E13510.333399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X321.536423 Y343.787117 Z4 E13521.214742 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X321.408 Y341.173 Z4 E13532.096085 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X321.438987 Y340.542247 Z4 E13534.721614 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009
G1 X321.536423 Y338.558883 Z4.992878 E13543.951895 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=4 matz1=4.992878 note=collision lift
G1 X321.920457 Y335.969941 Z6.301513 E13556.117607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=4.992878 matz1=6 note=collision lift
G1 X322.556401 Y333.431108 Z7.610148 E13568.283318 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X322.785804 Y332.789969 Z7.95062 E13571.448511 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X322.829001 Y332.669242 Z7.979619 E13571.995062 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X322.829488 Y332.66788 Z7.978896 E13572.001785 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X322.872198 Y332.548515 Z8 E13572.536112 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X322.872442 Y332.547834 Z8 E13572.53912 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X323.438133 Y330.966833 Z8 E13579.520246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X324.55716 Y328.600849 Z8 E13590.401589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X325.902705 Y326.355942 Z8 E13601.282933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X327.461811 Y324.253731 Z8 E13612.164276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X329.219462 Y322.314462 Z8 E13623.045619 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X331.158731 Y320.556811 Z8 E13633.926962 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X331.347115 Y320.417096 Z8 E13634.902064 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X333.260942 Y318.997705 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
G1 X335.505849 Y317.65216 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0009 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0009
G0 X335.505849 Y317.65216 Z12 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0008 note=intra-page lift
G0 X328.081201 Y304.194819 Z12 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0008 note=intra-page XY
G0 X328.081201 Y304.194819 Z5.624968 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0008 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0008
G1 X327.694475 Y303.549606 Z6.000136 E13634.999988 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=5.624968 matz1=6 note=collision lift
G1 X327.694335 Y303.549373 Z6 E13635.000059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X327.581268 Y303.360732 Z6 E13635.058022 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X327.3935 Y302.963731 Z6 E13635.213878 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X326.752168 Y301.607747 Z6 E13636.149319 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X326.606116 Y301.298946 Z6 E13636.44953 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X326.215862 Y300.208259 Z6 E13637.708388 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.83775 Y299.151506 Z6 E13639.282833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.745991 Y298.785185 Z6 E13639.891084 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.381521 Y297.330138 Z6 E13642.697408 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.283569 Y296.939094 Z6 E13643.55793 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.251559 Y296.723296 Z6 E13644.042403 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.251259 Y296.721274 Z6.001022 E13644.047547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.136236 Y295.945855 Z5.609072 E13646.12736 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=5.608439 note=collision lift
G1 X324.948912 Y294.683016 Z4.970746 E13649.970224 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=5.608439 matz1=4.970746 note=collision lift
G1 X324.945723 Y294.61811 Z4.938253 E13650.180939 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.970746 matz1=4.938253 note=collision lift
G1 X324.891398 Y293.512303 Z4.384684 E13653.995657 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.938253 matz1=4.384684 note=collision lift
G1 X324.87989 Y293.278054 Z4.267495 E13654.858145 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.384684 matz1=4.267495 note=collision lift
G1 X324.853692 Y292.744783 Z4.000714 E13656.892662 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.267495 matz1=4.000714 note=collision lift
G1 X324.853622 Y292.743357 Z4 E13656.898237 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.000714 matz1=4 note=collision lift
G1 X324.837 Y292.405 Z4 E13658.097069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X324.853622 Y292.066643 Z4 E13659.32771 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 note=prime ramp
G1 X324.853692 Y292.065217 Z4.000714 E13659.333585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4 matz1=4.000714 note=collision lift
G1 X324.863455 Y291.86649 Z4.100132 E13660.158979 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.000714 matz1=4.100132 note=collision lift
G1 X324.891398 Y291.297697 Z4.384684 E13662.597203 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.100132 matz1=4.384684 note=collision lift
G1 X324.92929 Y290.52639 Z4.770802 E13666.083441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.384684 matz1=4.770802 note=collision lift
G1 X324.948912 Y290.126984 Z4.970746 E13667.94222 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.770802 matz1=4.970746 note=collision lift
G1 X325.251259 Y288.088726 Z6.001022 E13677.520201 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.970746 matz1=6 note=collision lift
G1 X325.251559 Y288.086704 Z6 E13677.529701 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.283569 Y287.870906 Z6 E13678.436704 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X325.83775 Y285.658494 Z6 E13687.919018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X326.606116 Y283.511054 Z6 E13697.401331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X327.581268 Y281.449268 Z6 E13706.883644 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X327.693424 Y281.262147 Z6 E13707.790647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X327.694475 Y281.260394 Z6.001022 E13707.800147 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X328.753815 Y279.492992 Z4.970746 E13717.378128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=4.970746 note=collision lift
G1 X329.452049 Y278.551533 Z4.384684 E13722.826451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.970746 matz1=4.384684 note=collision lift
G1 X329.909811 Y277.934311 Z4.000714 E13726.397905 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.384684 matz1=4.000714 note=collision lift
G1 X329.910662 Y277.933164 Z4 E13726.404543 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.000714 matz1=4 note=collision lift
G1 X330.112464 Y277.661066 Z4 E13727.812964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X331.644131 Y275.971131 Z4 E13737.295277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X333.334066 Y274.439464 Z4 E13746.777591 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X333.490313 Y274.323583 Z4 E13747.586347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X335.165992 Y273.080815 Z5.043117 E13757.283678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4 matz1=5.043117 note=collision lift
G1 X337.122268 Y271.908268 Z6.183499 E13767.885227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=5.043117 matz1=6 note=collision lift
G1 X339.184054 Y270.933116 Z7.323881 E13778.486776 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X340.457246 Y270.477561 Z8 E13784.772309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X341.331494 Y270.16475 Z8 E13788.63267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X343.543906 Y269.610569 Z8 E13798.114984 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X344.091463 Y269.529347 Z8 E13800.416373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X344.096329 Y269.528625 Z8 E13800.436821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X344.843911 Y269.417732 Z7.682579 E13803.844799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X344.84478 Y269.417603 Z7.683019 E13803.848884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X345.593231 Y269.306581 Z7.338042 E13807.306165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X345.799984 Y269.275912 Z7.233534 E13808.277716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X345.803732 Y269.275728 Z7.231658 E13808.295158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X346.300492 Y269.251323 Z6.995331 E13810.5845 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X346.30207 Y269.251246 Z6.996121 E13810.591844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X348.078 Y269.164 Z6.107085 E13818.856758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X350.356016 Y269.275912 Z4.966704 E13829.458306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=4.966704 note=collision lift
G1 X352.268497 Y269.559602 Z4 E13838.445257 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.966704 matz1=4 note=collision lift
G1 X352.612094 Y269.610569 Z4 E13839.889397 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X354.824506 Y270.16475 Z4 E13849.37171 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X356.971946 Y270.933116 Z4 E13858.854024 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X359.033732 Y271.908268 Z4 E13868.336337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X360.990008 Y273.080815 Z4 E13877.81865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X362.821934 Y274.439464 Z4 E13887.300964 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X364.511869 Y275.971131 Z4 E13896.783277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X366.043536 Y277.661066 Z4 E13906.26559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X367.402185 Y279.492992 Z4 E13915.747904 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X368.574732 Y281.449268 Z4 E13925.230217 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X369.549884 Y283.511054 Z4 E13934.71253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X370.31825 Y285.658494 Z4 E13944.194844 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X370.872431 Y287.870906 Z4 E13953.677157 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X371.207088 Y290.126984 Z4 E13963.15947 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X371.319 Y292.405 Z4 E13972.641784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X371.207088 Y294.683016 Z4 E13982.124097 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X370.872431 Y296.939094 Z4 E13991.60641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X370.31825 Y299.151506 Z4 E14001.088724 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X369.549884 Y301.298946 Z4 E14010.571037 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X368.574732 Y303.360732 Z4 E14020.05335 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X367.402185 Y305.317008 Z4 E14029.535664 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X366.043536 Y307.148934 Z4 E14039.017977 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X364.511869 Y308.838869 Z4 E14048.50029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X362.821934 Y310.370536 Z4 E14057.982604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X360.990008 Y311.729185 Z4 E14067.464917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X359.033732 Y312.901732 Z4 E14076.94723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X356.971946 Y313.876884 Z4 E14086.429544 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X354.824506 Y314.64525 Z4 E14095.911857 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X352.612094 Y315.199431 Z4 E14105.39417 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X352.140075 Y315.269448 Z4 E14107.37807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X350.356016 Y315.534088 Z4.90179 E14115.761551 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4 matz1=4.90179 note=collision lift
G1 X348.078 Y315.646 Z6.042172 E14126.3631 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.90179 matz1=6 note=collision lift
G1 X345.799984 Y315.534088 Z7.182554 E14136.964648 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X345.593231 Y315.503419 Z7.287061 E14137.9362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X344.84478 Y315.392397 Z7.658606 E14141.440746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X344.843876 Y315.392263 Z7.658149 E14141.444995 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X344.096329 Y315.281375 Z8 E14144.893441 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X344.091089 Y315.280598 Z8 E14144.915464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X343.543906 Y315.199431 Z8 E14147.215278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X341.331494 Y314.64525 Z8 E14156.697592 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X340.457246 Y314.332439 Z8 E14160.557953 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X339.184054 Y313.876884 Z7.323881 E14166.843486 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X337.122268 Y312.901732 Z6.183499 E14177.445035 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X335.165992 Y311.729185 Z5.043117 E14188.046584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=5.043117 note=collision lift
G1 X333.490313 Y310.486417 Z4 E14197.743915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=5.043117 matz1=4 note=collision lift
G1 X333.334066 Y310.370536 Z4 E14198.552671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X331.644131 Y308.838869 Z4 E14208.034985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X331.560313 Y308.74639 Z4 E14208.553889 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008
G1 X330.251053 Y307.301844 Z4.974791 E14217.616029 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4 matz1=4.974791 note=collision lift
G1 X330.112464 Y307.148934 Z5.077976 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=4.974791 matz1=5.077976 note=collision lift
G1 X329.91076 Y306.876968 Z5.247276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=5.077976 matz1=5.247276 note=collision lift
G1 X328.753815 Y305.317008 Z7.18944 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=5.247276 matz1=6 note=collision lift
G1 X328.337104 Y304.621767 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
G1 X328.081201 Y304.194819 Z8 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0008 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0008
G0 X328.081201 Y304.194819 Z12 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0007 note=intra-page lift
G0 X315.715953 Y311.606263 Z12 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0007 note=intra-page XY
G0 X315.715953 Y311.606263 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0007 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0007
G1 X315.774252 Y311.497194 Z6 E14217.618149 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X316.647385 Y310.433278 Z6 E14217.927843 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X316.958808 Y310.053808 Z6 E14218.165331 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X317.738854 Y309.413641 Z6 E14218.863284 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X318.328014 Y308.930129 Z6 E14219.577528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X318.328027 Y308.930119 Z6.000009 E14219.577548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X318.401039 Y308.870199 Z5.952783 E14219.689209 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=5.952783 note=collision lift
G1 X318.402194 Y308.869252 Z5.953539 E14219.691003 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.952783 matz1=5.953539 note=collision lift
G1 X318.900323 Y308.602996 Z5.673253 E14220.422353 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.953539 matz1=5.673253 note=collision lift
G1 X318.90211 Y308.602041 Z5.672247 E14220.425176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.673253 matz1=5.672247 note=collision lift
G1 X319.482774 Y308.29167 Z6.001443 E14221.418859 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.672247 matz1=6 note=collision lift
G1 X319.485319 Y308.290309 Z6 E14221.423547 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X320.04894 Y307.989047 Z6 E14222.408611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X320.163111 Y307.954414 Z6 E14222.605049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X321.598522 Y307.518987 Z6 E14225.411373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X321.835765 Y307.44702 Z6 E14225.935253 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X323.081817 Y307.324295 Z6 E14228.841325 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X323.694 Y307.264 Z6 E14230.42825 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X324.574595 Y307.350731 Z6 E14232.894903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X325.552235 Y307.44702 Z6 E14235.887602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X326.047575 Y307.59728 Z6 E14237.57211 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X326.1638 Y307.632536 Z6 E14237.978113 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X326.166562 Y307.633374 Z6.001443 E14237.988957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X327.338938 Y307.98901 Z5.388892 E14242.852039 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=5.388892 note=collision lift
G1 X327.33906 Y307.989047 Z5.388956 E14242.852571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.388892 matz1=5.388956 note=collision lift
G1 X327.343355 Y307.991344 Z5.386521 E14242.872944 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.388956 matz1=5.386521 note=collision lift
G1 X327.905226 Y308.29167 Z5.068003 E14245.608453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.386521 matz1=5.068003 note=collision lift
G1 X328.526588 Y308.623795 Z4.715726 E14248.797406 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.068003 matz1=4.715726 note=collision lift
G1 X328.985806 Y308.869252 Z4.455375 E14251.217757 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.715726 matz1=4.455375 note=collision lift
G1 X329.482056 Y309.276513 Z4.13439 E14254.201789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.455375 matz1=4.13439 note=collision lift
G1 X329.689825 Y309.447025 Z4 E14255.451141 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.13439 matz1=4 note=collision lift
G1 X330.429192 Y310.053808 Z4 E14259.427713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X330.618319 Y310.284259 Z4 E14260.667159 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X331.613748 Y311.497194 Z4.784552 E14267.960743 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4 matz1=4.784552 note=collision lift
G1 X332.493953 Y313.14394 Z5.718166 E14276.640069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.784552 matz1=5.718166 note=collision lift
G1 X333.03598 Y314.930765 Z6.651779 E14285.319396 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.718166 matz1=6 note=collision lift
G1 X333.219 Y316.789 Z7.585392 E14293.998723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X333.137723 Y317.614223 Z8 E14297.853121 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X333.03598 Y318.647235 Z8 E14302.168668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X332.493953 Y320.43406 Z8 E14309.931694 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X331.795177 Y321.741377 Z8 E14316.094598 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X331.613748 Y322.080806 Z7.807563 E14317.883589 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X330.429192 Y323.524192 Z6.873949 E14326.562915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X328.985806 Y324.708748 Z7.807563 E14335.242242 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X328.646377 Y324.890177 Z8 E14337.031233 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X327.33906 Y325.588953 Z8 E14343.194137 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X325.552235 Y326.13098 Z8 E14350.957162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X324.519223 Y326.232723 Z8 E14355.27271 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X323.694 Y326.314 Z7.585392 E14359.127108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X321.835765 Y326.13098 Z6.651779 E14367.806434 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X320.04894 Y325.588953 Z5.718166 E14376.485761 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=5.718166 note=collision lift
G1 X318.402194 Y324.708748 Z4.784552 E14385.165088 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.718166 matz1=4.784552 note=collision lift
G1 X317.189259 Y323.713319 Z4 E14392.458671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.784552 matz1=4 note=collision lift
G1 X316.958808 Y323.524192 Z4 E14393.698118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X316.352025 Y322.784825 Z4 E14397.674689 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007
G1 X316.181513 Y322.577056 Z4.13439 E14398.924041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4 matz1=4.13439 note=collision lift
G1 X315.774252 Y322.080806 Z4.455375 E14401.908074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.13439 matz1=4.455375 note=collision lift
G1 X315.19667 Y321.000226 Z5.068003 E14407.603368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=4.455375 matz1=5.068003 note=collision lift
G1 X314.894047 Y320.43406 Z5.388956 E14410.587341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.068003 matz1=5.388956 note=collision lift
G1 X314.89401 Y320.433938 Z5.388892 E14410.587933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.388956 matz1=5.388892 note=collision lift
G1 X314.538374 Y319.261562 Z6.001443 E14416.28261 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=5.388892 matz1=6 note=collision lift
G1 X314.537536 Y319.2588 Z6 E14416.296027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X314.35202 Y318.647235 Z6 E14418.953026 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X314.169 Y316.789 Z6 E14426.716052 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X314.215923 Y316.312581 Z6 E14428.706354 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X314.35202 Y314.930765 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X314.894047 Y313.14394 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X315.121861 Y312.717731 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X315.122075 Y312.717331 Z6.000226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X315.122288 Y312.716932 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X315.195452 Y312.580051 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X315.19667 Y312.577774 Z6.001291 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X315.197887 Y312.575496 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
G1 X315.715953 Y311.606263 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0007 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0007
G0 X315.715953 Y311.606263 Z10 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0006 note=intra-page lift
G0 X294.001274 Y299.999525 Z10 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0006 note=intra-page XY
G0 X294.001274 Y299.999525 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0006 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0006
G1 X292.588958 Y299.49419 Z4 E14429.018168 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X292.311485 Y299.394909 Z4 E14429.152726 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X291.221906 Y298.879576 Z4 E14429.953609 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X290.689096 Y298.627576 Z4 E14430.491839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X289.908048 Y298.159433 Z4 E14431.512678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X289.149732 Y297.704916 Z4 E14432.723695 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X288.655034 Y297.338024 Z4 E14433.695375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X287.708216 Y296.635815 Z4 E14435.848293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X287.47022 Y296.420108 Z4 E14436.501699 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X286.378431 Y295.430569 Z4 E14439.865634 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X286.360632 Y295.410931 Z4 E14439.93165 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X285.353294 Y294.299504 Z4 E14443.985229 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X285.173185 Y294.100784 Z4 E14444.775716 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X284.4394 Y293.11139 Z4 E14448.662435 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X284.104084 Y292.659268 Z4 E14450.578542 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X283.622315 Y291.855486 Z4 E14453.963269 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X283.181424 Y291.119904 Z4 E14457.274109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X282.90676 Y290.539175 Z4 E14459.887731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=prime ramp
G1 X282.414091 Y289.497515 Z4 E14464.67841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X281.809475 Y287.807726 Z4 E14472.139902 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X281.373399 Y286.066812 Z4 E14479.601395 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X281.110062 Y284.291537 Z4 E14487.062887 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X281.022 Y282.499 Z4 E14494.52438 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X281.09175 Y281.079198 Z4 E14500.434351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X281.110062 Y280.706463 Z4.186592 E14502.169004 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4 matz1=4.186592 note=collision lift
G1 X281.373399 Y278.931188 Z5.083942 E14510.511207 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.186592 matz1=5.083942 note=collision lift
G1 X281.809475 Y277.190274 Z5.981292 E14518.853409 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.083942 matz1=5.981292 note=collision lift
G1 X282.414091 Y275.500485 Z6.878641 E14527.195611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.981292 matz1=6 note=collision lift
G1 X283.181424 Y273.878096 Z7.775991 E14535.537813 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X283.181467 Y273.878025 Z7.775949 E14535.538199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X283.34204 Y273.610124 Z7.927641 E14536.981792 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X283.342049 Y273.61011 Z7.927632 E14536.98187 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X283.356568 Y273.585886 Z7.941342 E14537.112388 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X283.356652 Y273.585746 Z7.941423 E14537.113148 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X283.418704 Y273.482218 Z8 E14537.670935 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X283.418707 Y273.482213 Z8 E14537.670956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X284.104084 Y272.338732 Z8 E14543.213554 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X285.173185 Y270.897216 Z8 E14550.675047 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X285.311828 Y270.744246 Z8 E14551.533366 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X286.378431 Y269.567431 Z7.205875 E14558.915938 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X287.708216 Y268.362185 Z6.308526 E14567.25814 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X287.71102 Y268.360105 Z6.30678 E14567.27437 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X289.149732 Y267.293084 Z7.202384 E14575.600342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X290.518008 Y266.47297 Z8 E14583.015374 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X290.689096 Y266.370424 Z8 E14583.84466 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X292.311485 Y265.603091 Z8 E14591.306153 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X294.001274 Y264.998475 Z8 E14598.767645 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X294.100476 Y264.973626 Z8 E14599.192824 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X295.742188 Y264.562399 Z7.153784 E14607.059662 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X297.517463 Y264.299062 Z6.256434 E14615.401864 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X298.029714 Y264.273896 Z6 E14617.785805 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X299.31 Y264.211 Z6 E14623.115036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X300.590286 Y264.273896 Z6 E14628.444267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X301.102537 Y264.299062 Z6.256434 E14630.828208 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X302.877812 Y264.562399 Z7.153784 E14639.17041 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X304.519524 Y264.973626 Z8 E14647.037248 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X304.618726 Y264.998475 Z8 E14647.462426 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X306.308515 Y265.603091 Z8 E14654.923919 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X307.930904 Y266.370424 Z8 E14662.385411 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X308.101992 Y266.47297 Z8 E14663.214698 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X309.470268 Y267.293084 Z7.202384 E14670.62973 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X310.90898 Y268.360105 Z6.30678 E14678.955702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X310.911784 Y268.362185 Z6.308526 E14678.971932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X312.241569 Y269.567431 Z7.205875 E14687.314134 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X313.308172 Y270.744246 Z8 E14694.696706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X313.446815 Y270.897216 Z8 E14695.555025 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X314.515916 Y272.338732 Z8 E14703.016518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X315.201293 Y273.482213 Z8 E14708.559116 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X315.201296 Y273.482218 Z8 E14708.559137 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X315.263348 Y273.585746 Z7.941423 E14709.116924 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X315.263432 Y273.585886 Z7.941342 E14709.117684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X315.277951 Y273.61011 Z7.927632 E14709.248202 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X315.27796 Y273.610124 Z7.927641 E14709.24828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X315.438533 Y273.878025 Z7.775949 E14710.691873 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X315.438576 Y273.878096 Z7.775991 E14710.692259 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X316.205909 Y275.500485 Z6.878641 E14719.034461 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=6 note=collision lift
G1 X316.810525 Y277.190274 Z5.981292 E14727.376663 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=6 matz1=5.981292 note=collision lift
G1 X317.246601 Y278.931188 Z5.083942 E14735.718865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.981292 matz1=5.083942 note=collision lift
G1 X317.509938 Y280.706463 Z4.186592 E14744.061067 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=5.083942 matz1=4.186592 note=collision lift
G1 X317.52825 Y281.079198 Z4 E14745.795721 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 matz0=4.186592 matz1=4 note=collision lift
G1 X317.598 Y282.499 Z4 E14751.705692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X317.509938 Y284.291537 Z4 E14759.167185 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X317.246601 Y286.066812 Z4 E14766.628677 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X316.810525 Y287.807726 Z4 E14774.090169 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X316.205909 Y289.497515 Z4 E14781.551662 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X315.438576 Y291.119904 Z4 E14789.013154 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X314.515916 Y292.659268 Z4 E14796.474647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X313.446815 Y294.100784 Z4 E14803.936139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X312.241569 Y295.430569 Z4 E14811.397632 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X310.911784 Y296.635815 Z4 E14818.859124 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X309.470268 Y297.704916 Z4 E14826.320617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X307.930904 Y298.627576 Z4 E14833.782109 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X306.308515 Y299.394909 Z4 E14841.243602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X304.618726 Y299.999525 Z4 E14848.705094 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X302.877812 Y300.435601 Z4 E14856.166586 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X301.102537 Y300.698938 Z4 E14863.628079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X299.31 Y300.787 Z4 E14871.089571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X298.926365 Y300.768153 Z4 E14872.686464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006
G1 X297.517463 Y300.698938 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
G1 X295.742188 Y300.435601 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
G1 X294.001274 Y299.999525 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0006 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0006
G0 X294.001274 Y299.999525 Z8.845099 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0005 note=intra-page lift
G0 X286.197707 Y321.997357 Z8.845099 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0005 note=intra-page XY
G0 X286.197707 Y321.997357 Z4.845099 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0005 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0005
G1 X286.221122 Y321.979991 Z4.859618 E14872.686611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.845099 matz1=4.859618 note=collision lift
G1 X286.221123 Y321.97999 Z4.859665 E14872.686612 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.859618 matz1=4.859665 note=collision lift
G1 X286.39776 Y321.848987 Z4.969622 E14872.697212 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.859665 matz1=4.969622 note=collision lift
G1 X286.397992 Y321.848815 Z4.970746 E14872.697302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.969622 matz1=4.970746 note=collision lift
G1 X287.334218 Y321.287663 Z5.516502 E14872.998278 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.970746 matz1=5.515961 note=collision lift
G1 X288.165394 Y320.789475 Z6.001022 E14873.611383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=5.515961 matz1=6 note=collision lift
G1 X288.167147 Y320.788424 Z6 E14873.61302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X288.354268 Y320.676268 Z6 E14873.775965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X288.531571 Y320.59241 Z6 E14873.933719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X289.887555 Y319.951077 Z6 E14875.492788 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X290.416054 Y319.701116 Z6 E14876.269338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X291.277915 Y319.392737 Z6 E14877.675485 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X292.563494 Y318.93275 Z6 E14880.204506 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X292.694066 Y318.900043 Z6 E14880.481808 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X294.149113 Y318.535573 Z6 E14883.91176 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X294.775906 Y318.378569 Z6 E14885.581468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X294.991704 Y318.346559 Z6 E14886.171336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X294.993726 Y318.346259 Z6.001022 E14886.177584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X295.554123 Y318.263132 Z5.717759 E14887.965339 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=5.717018 note=collision lift
G1 X296.881243 Y318.066272 Z5.04694 E14892.642545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=5.717018 matz1=5.046865 note=collision lift
G1 X297.031984 Y318.043912 Z4.970746 E14893.213243 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=5.046865 matz1=4.970746 note=collision lift
G1 X298.202697 Y317.986398 Z4.384684 E14897.871782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.970746 matz1=4.384684 note=collision lift
G1 X298.219805 Y317.985558 Z4.376125 E14897.943379 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.384684 matz1=4.376125 note=collision lift
G1 X298.970217 Y317.948692 Z4.000714 E14901.183799 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.376125 matz1=4.000714 note=collision lift
G1 X298.971643 Y317.948622 Z4 E14901.190145 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.000714 matz1=4 note=collision lift
G1 X299.31 Y317.932 Z4 E14902.552639 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X299.629366 Y317.947689 Z4 E14903.867841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 note=prime ramp
G1 X299.648357 Y317.948622 Z4 E14903.946891 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X299.649783 Y317.948692 Z4.000714 E14903.953528 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4 matz1=4.000714 note=collision lift
G1 X300.417303 Y317.986398 Z4.384684 E14907.524982 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.000714 matz1=4.384684 note=collision lift
G1 X301.588016 Y318.043912 Z4.970746 E14912.973306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.384684 matz1=4.970746 note=collision lift
G1 X303.626274 Y318.346259 Z6.001022 E14922.551287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.970746 matz1=6 note=collision lift
G1 X303.628296 Y318.346559 Z6 E14922.560787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X303.844094 Y318.378569 Z6 E14923.46779 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X306.056506 Y318.93275 Z6 E14932.950103 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X308.203946 Y319.701116 Z6 E14942.432416 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X310.265732 Y320.676268 Z6 E14951.91473 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X310.452853 Y320.788424 Z6 E14952.821732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X310.454606 Y320.789475 Z6.001022 E14952.831232 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X312.222008 Y321.848815 Z4.970746 E14962.409213 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=4.970746 note=collision lift
G1 X313.163467 Y322.547049 Z4.384684 E14967.857537 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.970746 matz1=4.384684 note=collision lift
G1 X313.780689 Y323.004811 Z4.000714 E14971.428991 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.384684 matz1=4.000714 note=collision lift
G1 X313.781836 Y323.005662 Z4 E14971.435628 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.000714 matz1=4 note=collision lift
G1 X314.053934 Y323.207464 Z4 E14972.844049 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X315.743869 Y324.739131 Z4 E14982.326363 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X317.275536 Y326.429066 Z4 E14991.808676 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X317.391417 Y326.585313 Z4 E14992.617433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X318.634185 Y328.260992 Z5.043117 E15002.314764 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4 matz1=5.043117 note=collision lift
G1 X319.806732 Y330.217268 Z6.183499 E15012.916312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=5.043117 matz1=6 note=collision lift
G1 X320.781884 Y332.279054 Z7.323881 E15023.517861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X321.237439 Y333.552246 Z8 E15029.803394 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X321.55025 Y334.426494 Z8 E15033.663756 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.104431 Y336.638906 Z8 E15043.146069 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.185653 Y337.186464 Z8 E15045.44746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.186375 Y337.191329 Z8 E15045.467906 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.297268 Y337.938911 Z7.682608 E15048.875839 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.297397 Y337.93978 Z7.683047 E15048.879923 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.408419 Y338.688231 Z7.338101 E15052.337151 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.439088 Y338.894984 Z7.233593 E15053.308702 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.439254 Y338.89835 Z7.231908 E15053.324368 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.463677 Y339.39549 Z6.995422 E15055.615425 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.463754 Y339.39707 Z6.996212 E15055.622775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.551 Y341.173 Z6.107177 E15063.887689 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X322.439088 Y343.451016 Z4.966795 E15074.489238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=4.966795 note=collision lift
G1 X322.155372 Y345.363678 Z4 E15083.477036 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.966795 matz1=4 note=collision lift
G1 X322.104431 Y345.707094 Z4 E15084.920418 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X321.55025 Y347.919506 Z4 E15094.402731 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X320.781884 Y350.066946 Z4 E15103.885045 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X319.806732 Y352.128732 Z4 E15113.367358 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X318.634185 Y354.085008 Z4 E15122.849671 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X317.275536 Y355.916934 Z4 E15132.331985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X315.743869 Y357.606869 Z4 E15141.814298 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X314.053934 Y359.138536 Z4 E15151.296611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X312.222008 Y360.497185 Z4 E15160.778925 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X310.265732 Y361.669732 Z4 E15170.261238 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X308.203946 Y362.644884 Z4 E15179.743551 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X306.056506 Y363.41325 Z4 E15189.225865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X303.844094 Y363.967431 Z4 E15198.708178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X301.588016 Y364.302088 Z4 E15208.190491 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X299.31 Y364.414 Z4 E15217.672805 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X297.031984 Y364.302088 Z4 E15227.155118 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X294.775906 Y363.967431 Z4 E15236.637431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X292.563494 Y363.41325 Z4 E15246.119744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X290.416054 Y362.644884 Z4 E15255.602058 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X288.354268 Y361.669732 Z4 E15265.084371 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X286.397992 Y360.497185 Z4 E15274.566684 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X284.566066 Y359.138536 Z4 E15284.048998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X282.876131 Y357.606869 Z4 E15293.531311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X281.344464 Y355.916934 Z4 E15303.013624 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X279.985815 Y354.085008 Z4 E15312.495938 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X278.813268 Y352.128732 Z4 E15321.978251 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X277.838116 Y350.066946 Z4 E15331.460564 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X277.06975 Y347.919506 Z4 E15340.942878 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X276.515569 Y345.707094 Z4 E15350.425191 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X276.180912 Y343.451016 Z4 E15359.907504 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X276.069 Y341.173 Z4 E15369.389818 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X276.180912 Y338.894984 Z4 E15378.872131 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X276.515569 Y336.638906 Z4 E15388.354444 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X277.06975 Y334.426494 Z4 E15397.836758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X277.838116 Y332.279054 Z4 E15407.319071 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X278.813268 Y330.217268 Z4 E15416.801384 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X279.985815 Y328.260992 Z4 E15426.283698 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X280.081327 Y328.132208 Z4 E15426.950302 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005
G1 X280.77873 Y327.19187 Z4.585364 E15432.392136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4 matz1=4.585364 note=collision lift
G1 X280.804688 Y327.15687 Z4.604641 E15432.590236 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.585364 matz1=4.604641 note=collision lift
G1 X280.842353 Y327.106085 Z4.636255 E15432.884136 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.604641 matz1=4.636255 note=collision lift
G1 X280.969598 Y326.934514 Z4.671908 E15433.784498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.636255 matz1=4.671908 note=collision lift
G1 X280.971928 Y326.931372 Z4.669952 E15433.80268 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.671908 matz1=4.669952 note=collision lift
G1 X281.096844 Y326.762943 Z4.672735 E15434.67457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.669952 matz1=4.672735 note=collision lift
G1 X281.097832 Y326.761611 Z4.671906 E15434.682277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.672735 matz1=4.671906 note=collision lift
G1 X281.22409 Y326.591372 Z4.656875 E15435.565673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.671906 matz1=4.656875 note=collision lift
G1 X281.22485 Y326.590346 Z4.656236 E15435.571606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.656875 matz1=4.656236 note=collision lift
G1 X281.342216 Y326.432097 Z4.631504 E15436.397158 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.656236 matz1=4.631504 note=collision lift
G1 X281.344464 Y326.429066 Z4.633391 E15436.414699 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.631504 matz1=4.633391 note=collision lift
G1 X281.427947 Y326.336956 Z4.60135 E15436.94842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.633391 matz1=4.60135 note=collision lift
G1 X281.690779 Y326.046966 Z4.696164 E15438.622641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.60135 matz1=4.696164 note=collision lift
G1 X281.692368 Y326.045213 Z4.69853 E15438.636549 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.696164 matz1=4.69853 note=collision lift
G1 X282.200442 Y325.484639 Z4.845044 E15441.840398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.69853 matz1=4.845044 note=collision lift
G1 X282.204138 Y325.480562 Z4.845044 E15441.863277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.845044 matz1=4.845044 note=collision lift
G1 X282.708517 Y324.924065 Z4.961038 E15445.022828 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.845044 matz1=4.961038 note=collision lift
G1 X282.718734 Y324.912792 Z4.961038 E15445.086083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.961038 matz1=4.961038 note=collision lift
G1 X282.766014 Y324.860628 Z4.996239 E15445.413329 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.961038 matz1=4.996239 note=collision lift
G1 X282.876131 Y324.739131 Z5.078226 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=4.996239 matz1=5.078226 note=collision lift
G1 X284.566066 Y323.207464 Z6.218607 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=5.078226 matz1=6 note=collision lift
G1 X284.838203 Y323.005633 Z6.388014 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X284.839311 Y323.004811 Z6.389394 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X285.217112 Y322.724615 Z6.859618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
G1 X286.197707 Y321.997357 Z6.859249 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0005 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0005
G0 X286.197707 Y321.997357 Z10.859249 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0004 note=intra-page lift
G0 X276.325793 Y308.686622 Z10.859249 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0004 note=intra-page XY
G0 X276.325793 Y308.686622 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0004 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0004
G1 X275.867546 Y308.068747 Z6 E15445.495337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X275.49187 Y307.441969 Z6 E15445.725143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X274.720716 Y306.155377 Z6 E15446.660584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X274.445112 Y305.69556 Z6 E15447.146169 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X274.032986 Y304.824192 Z6 E15448.219653 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X273.549229 Y303.801374 Z6 E15449.808271 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X273.549195 Y303.801302 Z6.00004 E15449.80841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X273.408289 Y303.503382 Z5.835259 E15450.402349 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=5.835247 note=collision lift
G1 X273.349252 Y303.378559 Z5.766219 E15450.662384 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.835247 matz1=5.766219 note=collision lift
G1 X273.26214 Y303.194377 Z5.86809 E15451.058142 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.766219 matz1=5.86809 note=collision lift
G1 X273.261634 Y303.192961 Z5.867338 E15451.061116 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.86809 matz1=5.867338 note=collision lift
G1 X273.172249 Y302.943146 Z6 E15451.598188 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.867338 matz1=6 note=collision lift
G1 X272.896165 Y302.171544 Z6 E15453.208673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X272.39083 Y300.759228 Z6 E15456.638625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X272.330024 Y300.589286 Z6 E15457.093381 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X272.00941 Y299.309323 Z6 E15460.692204 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X271.65774 Y297.905377 Z6 E15465.194584 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X271.65001 Y297.853268 Z6 E15465.36941 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X271.429914 Y296.369503 Z6 E15470.670244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X271.365727 Y295.936783 Z6 E15472.333617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X271.365708 Y295.936658 Z6.000063 E15472.334162 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X271.251829 Y295.168951 Z5.612009 E15475.790535 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=5.612009 note=collision lift
G1 X271.251762 Y295.168495 Z5.612239 E15475.792647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.612009 matz1=5.612239 note=collision lift
G1 X271.24324 Y294.995029 Z5.525402 E15476.594706 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.612239 matz1=5.525402 note=collision lift
G1 X271.129093 Y292.671507 Z4.362247 E15487.408021 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.525402 matz1=4.362247 note=collision lift
G1 X271.116 Y292.405 Z4.228833 E15488.648303 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=4.362247 matz1=4.228833 note=collision lift
G1 X271.129093 Y292.138493 Z4.362247 E15489.888585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=4.228833 matz1=4.362247 note=collision lift
G1 X271.251762 Y289.641505 Z5.612239 E15501.509185 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=4.362247 matz1=5.612239 note=collision lift
G1 X271.251829 Y289.641049 Z5.612009 E15501.511324 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.612239 matz1=5.612009 note=collision lift
G1 X271.365708 Y288.873342 Z6.000063 E15505.118865 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.612009 matz1=6 note=collision lift
G1 X271.365727 Y288.873217 Z6 E15505.119451 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X271.65774 Y286.904623 Z6 E15513.393465 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X272.330024 Y284.220714 Z6 E15524.896599 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X272.980122 Y282.403812 Z6 E15532.919376 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X273.26214 Y281.615623 Z6.418562 E15536.810534 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X274.445112 Y279.11444 Z7.801976 E15549.671429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X274.648721 Y278.774739 Z8 E15551.512357 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X275.867546 Y276.741253 Z8 E15561.368915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X276.302825 Y276.154346 Z8 E15564.406827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X277.515743 Y274.518916 Z6.981938 E15573.871233 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X279.373831 Y272.468831 Z5.598524 E15586.732128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=5.598524 note=collision lift
G1 X281.423916 Y270.610743 Z6.981938 E15599.593023 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.598524 matz1=6 note=collision lift
G1 X283.059346 Y269.397825 Z8 E15609.057429 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X283.646253 Y268.962546 Z8 E15612.095341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X285.679739 Y267.743721 Z8 E15621.951899 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X286.01944 Y267.540112 Z7.801976 E15623.792827 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X286.804927 Y267.168605 Z7.36752 E15627.831739 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X287.948436 Y266.627765 Z8 E15633.711579 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X288.520623 Y266.35714 Z8 E15636.343112 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X291.125714 Y265.425024 Z8 E15647.846246 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X293.809623 Y264.75274 Z8 E15659.34938 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X296.546505 Y264.346762 Z8 E15670.852515 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X299.31 Y264.211 Z8 E15682.355649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X302.073495 Y264.346762 Z8 E15693.858783 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X304.810377 Y264.75274 Z8 E15705.361917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X307.494286 Y265.425024 Z8 E15716.865051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X310.099377 Y266.35714 Z8 E15728.368186 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X310.671564 Y266.627765 Z8 E15730.999719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X311.815073 Y267.168605 Z7.36752 E15736.879559 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X312.60056 Y267.540112 Z7.801976 E15740.91847 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X312.940261 Y267.743721 Z8 E15742.759399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X314.973747 Y268.962546 Z8 E15752.615956 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X315.560654 Y269.397825 Z8 E15755.653868 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X317.196084 Y270.610743 Z6.981938 E15765.118275 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X319.246169 Y272.468831 Z5.598524 E15777.97917 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=5.598524 note=collision lift
G1 X321.104257 Y274.518916 Z6.981938 E15790.840065 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.598524 matz1=6 note=collision lift
G1 X322.317175 Y276.154346 Z8 E15800.304471 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X322.752454 Y276.741253 Z8 E15803.342383 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X323.971279 Y278.774739 Z8 E15813.19894 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X324.174888 Y279.11444 Z7.801976 E15815.039869 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X324.889954 Y280.62632 Z6.965749 E15822.813842 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X325.35786 Y281.615623 Z7.512937 E15827.900764 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X325.686033 Y282.532806 Z8 E15832.428743 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X326.289976 Y284.220714 Z8 E15839.88193 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X326.888244 Y286.609136 Z8 E15850.118616 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X326.96226 Y286.904623 Z7.847692 E15851.534548 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X327.368238 Y289.641505 Z6.464278 E15864.395443 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X327.504 Y292.405 Z5.080864 E15877.256338 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=5.080864 note=collision lift
G1 X327.368238 Y295.168495 Z6.464278 E15890.117233 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.080864 matz1=6 note=collision lift
G1 X326.96226 Y297.905377 Z7.847692 E15902.978128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X326.888244 Y298.200864 Z8 E15904.394059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X326.289976 Y300.589286 Z8 E15914.630746 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X325.686033 Y302.277194 Z8 E15922.083932 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X325.35786 Y303.194377 Z7.512937 E15926.611911 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X324.889954 Y304.18368 Z6.965749 E15931.698834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X324.174888 Y305.69556 Z7.801976 E15939.472806 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X323.971279 Y306.035261 Z8 E15941.313735 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X322.752454 Y308.068747 Z8 E15951.170293 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X322.317175 Y308.655654 Z8 E15954.208205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X321.104257 Y310.291084 Z6.981938 E15963.672611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X319.246169 Y312.341169 Z5.598524 E15976.533506 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=5.598524 note=collision lift
G1 X317.196084 Y314.199257 Z6.981938 E15989.394401 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.598524 matz1=6 note=collision lift
G1 X315.560654 Y315.412175 Z8 E15998.858807 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X314.973747 Y315.847454 Z8 E16001.896719 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X312.940261 Y317.066279 Z8 E16011.753277 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X312.60056 Y317.269888 Z7.801976 E16013.594205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X311.08868 Y317.984954 Z6.965749 E16021.368178 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X310.099377 Y318.45286 Z7.512937 E16026.4551 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X309.182194 Y318.781033 Z8 E16030.983079 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X307.494286 Y319.384976 Z8 E16038.436266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X305.105864 Y319.983244 Z8 E16048.672952 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X304.810377 Y320.05726 Z7.847692 E16050.088884 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X302.073495 Y320.463238 Z6.464278 E16062.949779 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X299.31 Y320.599 Z5.080864 E16075.810674 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=5.080864 note=collision lift
G1 X296.546505 Y320.463238 Z6.464278 E16088.671569 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.080864 matz1=6 note=collision lift
G1 X293.809623 Y320.05726 Z7.847692 E16101.532464 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X293.514136 Y319.983244 Z8 E16102.948396 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X291.125714 Y319.384976 Z8 E16113.185082 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X289.437806 Y318.781033 Z8 E16120.638269 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X288.520623 Y318.45286 Z7.512937 E16125.166248 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X286.01944 Y317.269888 Z6.129523 E16138.027143 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X285.79725 Y317.136712 Z6 E16139.231249 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X283.646253 Y315.847454 Z6 E16149.657398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X281.638234 Y314.358206 Z6 E16160.05119 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
G1 X281.425124 Y314.200153 Z5.867338 E16161.284482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=5.867338 note=collision lift
G1 X281.423916 Y314.199257 Z5.86809 E16161.291472 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.867338 matz1=5.86809 note=collision lift
G1 X279.571538 Y312.520359 Z4.618097 E16172.912071 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.86809 matz1=4.618097 note=collision lift
G1 X279.373831 Y312.341169 Z4.484683 E16174.152354 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=4.618097 matz1=4.484683 note=collision lift
G1 X279.373509 Y312.340813 Z4.484443 E16174.154585 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=4.484683 matz1=4.484443 note=collision lift
G1 X279.300528 Y312.26029 Z4.53878 E16174.659732 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=4.484443 matz1=4.53878 note=collision lift
G1 X277.854458 Y310.664798 Z5.615432 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=4.53878 matz1=5.615432 note=collision lift
G1 X277.515743 Y310.291084 Z5.866647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.615432 matz1=5.866647 note=collision lift
G1 X277.515707 Y310.291035 Z5.866617 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.866647 matz1=5.866617 note=collision lift
G1 X277.356798 Y310.076771 Z5.999997 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.866617 matz1=5.999997 note=collision lift
G1 X277.356794 Y310.076766 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=5.999997 matz1=6 note=collision lift
G1 X276.325793 Y308.686622 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0004 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0004
G0 X276.325793 Y308.686622 Z10 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0003 note=intra-page lift
G0 X265.401 Y316.789 Z10 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0003 note=intra-page XY
G0 X265.401 Y316.789 Z6 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0003 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0003
G1 X265.533626 Y315.442429 Z6 E16174.913457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.533684 Y315.441833 Z6.000885 E16174.913858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.533858 Y315.440071 Z6 E16174.914602 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.547959 Y315.296899 Z6 E16174.971545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.58402 Y314.930765 Z6 E16175.143261 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.91265 Y313.847418 Z6 E16175.906987 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X266.126047 Y313.14394 Z6 E16176.593145 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X266.486604 Y312.469387 Z6 E16177.466056 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X267.006252 Y311.497194 Z6 E16179.009384 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X267.258513 Y311.189812 Z6 E16179.648752 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X267.412034 Y311.002747 Z6 E16180.059309 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X267.413513 Y311.000944 Z6.001166 E16180.063821 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X268.15197 Y310.101132 Z5.531019 E16182.455076 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=5.53096 note=collision lift
G1 X268.190736 Y310.053896 Z5.506338 E16182.592672 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.53096 matz1=5.506338 note=collision lift
G1 X268.190808 Y310.053808 Z5.506395 E16182.592939 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.506338 matz1=5.506395 note=collision lift
G1 X268.686939 Y309.646643 Z5.247189 E16184.110886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.506395 matz1=5.247189 note=collision lift
G1 X268.687057 Y309.646547 Z5.247265 E16184.111276 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.247189 matz1=5.247265 note=collision lift
G1 X268.831769 Y309.527785 Z5.153664 E16184.596428 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.247265 matz1=5.153664 note=collision lift
G1 X269.199813 Y309.225739 Z5.391724 E16185.885027 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.153664 matz1=5.391724 note=collision lift
G1 X269.634194 Y308.869252 Z5.67269 E16187.50693 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.391724 matz1=5.67269 note=collision lift
G1 X270.321834 Y308.5017 Z6.062544 E16189.938606 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.67269 matz1=5.809367 note=collision lift
G1 X271.28094 Y307.989047 Z6.606303 E16193.682023 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.809367 matz1=6 note=collision lift
G1 X271.52412 Y307.91528 Z6.733364 E16194.615813 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X272.80799 Y307.525822 Z7.404185 E16199.916647 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X273.067765 Y307.44702 Z7.539917 E16201.06506 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X273.9835 Y307.356828 Z8 E16205.147722 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X274.150409 Y307.340389 Z8 E16205.841108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X274.926 Y307.264 Z8 E16209.081241 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X276.784235 Y307.44702 Z8 E16216.844267 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X277.014508 Y307.516873 Z8 E16217.844708 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X278.57106 Y307.989047 Z7.186704 E16225.405508 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X280.217806 Y308.869252 Z6.253091 E16234.084834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X281.661192 Y310.053808 Z5.319477 E16242.764161 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=5.319477 note=collision lift
G1 X282.845748 Y311.497194 Z6.253091 E16251.443488 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.319477 matz1=6 note=collision lift
G1 X283.725953 Y313.14394 Z7.186704 E16260.122814 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X284.198127 Y314.700492 Z8 E16267.683613 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X284.26798 Y314.930765 Z8 E16268.684055 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X284.451 Y316.789 Z8 E16276.447081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X284.358172 Y317.7315 Z8 E16280.384498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X284.26798 Y318.647235 Z7.539917 E16284.661658 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X283.725953 Y320.43406 Z6.606303 E16293.340985 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X282.845748 Y322.080806 Z5.67269 E16302.020312 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=5.67269 note=collision lift
G1 X281.661192 Y323.524192 Z4.739077 E16310.699638 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.67269 matz1=4.739077 note=collision lift
G1 X281.34281 Y323.785482 Z4.53314 E16312.614125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.739077 matz1=4.53314 note=collision lift
G1 X280.714056 Y324.301487 Z4.939832 E16316.394933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.53314 matz1=4.939832 note=collision lift
G1 X280.217806 Y324.708748 Z5.260785 E16319.378906 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=4.939832 matz1=5.260785 note=collision lift
G1 X280.217694 Y324.708808 Z5.260722 E16319.379498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.260785 matz1=5.260722 note=collision lift
G1 X279.137226 Y325.28633 Z5.873273 E16325.074175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.260722 matz1=5.873273 note=collision lift
G1 X279.135332 Y325.287343 Z5.872199 E16325.084159 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.873273 matz1=5.872199 note=collision lift
G1 X278.57106 Y325.588953 Z5.916113 E16327.750486 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.872199 matz1=5.916113 note=collision lift
G1 X278.57103 Y325.588961 Z5.916098 E16327.750629 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.916113 matz1=5.916098 note=collision lift
G1 X277.398562 Y325.944626 Z6.000198 E16332.856514 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=5.916098 matz1=6 note=collision lift
G1 X277.398183 Y325.944741 Z6 E16332.858356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X276.784235 Y326.13098 Z6 E16335.525708 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X274.926 Y326.314 Z6 E16343.288734 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X273.922064 Y326.215121 Z6 E16347.482808 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X273.906068 Y326.213545 Z6.008037 E16347.557526 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X273.890071 Y326.21197 Z6 E16347.632243 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X273.067765 Y326.13098 Z6 E16351.067536 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X271.28094 Y325.588953 Z6 E16358.830561 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X269.634194 Y324.708748 Z6 E16366.593587 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X268.283342 Y323.600133 Z6 E16373.858933 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X268.190808 Y323.524192 Z6 E16374.356613 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X268.114868 Y323.431659 Z6 E16374.854287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X267.006252 Y322.080806 Z6 E16382.119639 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X266.720833 Y321.546826 Z6 E16384.636908 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X266.126047 Y320.43406 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.58402 Y318.647235 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.50303 Y317.824929 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.501455 Y317.808932 Z6.008037 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.499879 Y317.792936 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
G1 X265.401 Y316.789 Z6 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0003 matz0=6 matz1=6 note=collision lift
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0003
G0 X265.401 Y316.789 Z10 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0002 note=intra-page lift
G0 X248.263984 Y315.534088 Z10 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0002 note=intra-page XY
G0 X248.263984 Y315.534088 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0002 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0002
G1 X246.780219 Y315.313993 Z4 E16384.948722 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X246.007906 Y315.199431 Z4 E16385.357805 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X245.310224 Y315.024671 Z4 E16385.884163 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X243.855177 Y314.6602 Z4 E16387.443232 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X243.795494 Y314.64525 Z4 E16387.520497 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X242.441108 Y314.160643 Z4 E16389.625928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X241.648054 Y313.876884 Z4 E16391.124983 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X241.053492 Y313.595677 Z4 E16392.432252 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X239.697508 Y312.954345 Z4 E16395.862203 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X239.586268 Y312.901732 Z4 E16396.171263 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X238.405223 Y312.193841 Z4 E16399.915782 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X237.629992 Y311.729185 Z4 E16402.659337 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X237.151134 Y311.37404 Z4 E16404.592989 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X235.946323 Y310.480491 Z4 E16409.893823 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X235.798066 Y310.370536 Z4 E16410.589206 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X234.823405 Y309.487155 Z4 E16415.818285 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=prime ramp
G1 X234.108131 Y308.838869 Z4 E16419.831725 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X232.576464 Y307.148934 Z4 E16429.314038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X231.217815 Y305.317008 Z4 E16438.796351 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X230.045268 Y303.360732 Z4 E16448.278665 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X229.070116 Y301.298946 Z4 E16457.760978 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X228.30175 Y299.151506 Z4 E16467.243291 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X227.747569 Y296.939094 Z4 E16476.725605 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X227.412912 Y294.683016 Z4 E16486.207918 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X227.301 Y292.405 Z4 E16495.690231 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X227.412912 Y290.126984 Z4 E16505.172545 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X227.747569 Y287.870906 Z4 E16514.654858 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X228.30175 Y285.658494 Z4 E16524.137171 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X229.070116 Y283.511054 Z4 E16533.619485 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X230.045268 Y281.449268 Z4 E16543.101798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X231.217815 Y279.492992 Z4 E16552.584111 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X232.576464 Y277.661066 Z4 E16562.066424 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X234.108131 Y275.971131 Z4 E16571.548738 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X235.798066 Y274.439464 Z4 E16581.031051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X237.629992 Y273.080815 Z4 E16590.513364 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X239.586268 Y271.908268 Z4 E16599.995678 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X241.648054 Y270.933116 Z4 E16609.477991 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X243.795494 Y270.16475 Z4 E16618.960304 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X246.007906 Y269.610569 Z4 E16628.442618 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X246.351322 Y269.559628 Z4 E16629.886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X248.263984 Y269.275912 Z4.966795 E16638.873798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=4 matz1=4.966795 note=collision lift
G1 X250.542 Y269.164 Z6.107177 E16649.475347 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=4.966795 matz1=6 note=collision lift
G1 X252.31793 Y269.251246 Z6.996212 E16657.740261 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X252.31951 Y269.251323 Z6.995422 E16657.747611 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X252.81665 Y269.275746 Z7.231908 E16660.038668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X252.820016 Y269.275912 Z7.233593 E16660.054333 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X253.026769 Y269.306581 Z7.338101 E16661.025885 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X253.77522 Y269.417603 Z7.683047 E16664.483112 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X253.776089 Y269.417732 Z7.682608 E16664.487197 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X254.523671 Y269.528625 Z8 E16667.895129 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X254.528536 Y269.529347 Z8 E16667.915576 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X255.076094 Y269.610569 Z8 E16670.216967 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X257.288506 Y270.16475 Z8 E16679.69928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X258.162754 Y270.477561 Z8 E16683.559642 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X259.435946 Y270.933116 Z7.323881 E16689.845175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X261.497732 Y271.908268 Z6.183499 E16700.446723 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X263.454008 Y273.080815 Z5.043117 E16711.048272 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=5.043117 note=collision lift
G1 X265.129687 Y274.323583 Z4 E16720.745603 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.043117 matz1=4 note=collision lift
G1 X265.285934 Y274.439464 Z4 E16721.55436 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X266.975869 Y275.971131 Z4 E16731.036673 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X267.05266 Y276.055858 Z4 E16731.512077 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X268.507536 Y277.661066 Z5.083208 E16741.582108 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=4 matz1=5.083208 note=collision lift
G1 X269.866185 Y279.492992 Z6.22359 E16752.183656 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.083208 matz1=6 note=collision lift
G1 X271.038732 Y281.449268 Z7.363971 E16762.785205 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X271.582607 Y282.599194 Z8 E16768.698038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X272.013884 Y283.511054 Z8 E16772.891753 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X272.78225 Y285.658494 Z8 E16782.374066 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X273.020374 Y286.609136 Z8 E16786.448482 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X273.336431 Y287.870906 Z7.349624 E16792.494695 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X273.671088 Y290.126984 Z6.209242 E16803.096244 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X273.783 Y292.405 Z5.068861 E16813.697792 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=5.068861 note=collision lift
G1 X273.671088 Y294.683016 Z6.209242 E16824.299341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.068861 matz1=6 note=collision lift
G1 X273.336431 Y296.939094 Z7.349624 E16834.90089 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X273.020374 Y298.200864 Z8 E16840.947102 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X272.78225 Y299.151506 Z8 E16845.021518 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X272.013884 Y301.298946 Z8 E16854.503832 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X271.582607 Y302.210806 Z8 E16858.697546 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X271.038732 Y303.360732 Z7.363971 E16864.61038 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X269.866185 Y305.317008 Z6.22359 E16875.211928 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=6 note=collision lift
G1 X268.507536 Y307.148934 Z5.083208 E16885.813477 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=6 matz1=5.083208 note=collision lift
G1 X267.798637 Y307.931084 Z4.555407 E16890.720175 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.083208 matz1=4.555407 note=collision lift
G1 X266.975869 Y308.838869 Z5.140344 E16896.364565 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=4.555407 matz1=5.140344 note=collision lift
G1 X266.975544 Y308.839163 Z5.140125 E16896.366604 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.140344 matz1=5.140125 note=collision lift
G1 X266.849719 Y308.953204 Z5.212271 E16897.13369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.140125 matz1=5.212271 note=collision lift
G1 X266.849693 Y308.953228 Z5.212253 E16897.133851 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.212271 matz1=5.212253 note=collision lift
G1 X266.814328 Y308.985281 Z5.232463 E16897.349342 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.212253 matz1=5.232463 note=collision lift
G1 X266.790935 Y309.006483 Z5.248249 E16897.496095 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.232463 matz1=5.248249 note=collision lift
G1 X266.232664 Y309.51247 Z5.458571 E16900.748336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.248249 matz1=5.458571 note=collision lift
G1 X266.230361 Y309.514558 Z5.460125 E16900.762785 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.458571 matz1=5.460125 note=collision lift
G1 X265.669787 Y310.022632 Z5.647346 E16904.003074 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.460125 matz1=5.647346 note=collision lift
G1 X265.668272 Y310.024005 Z5.646324 E16904.012578 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.647346 matz1=5.646324 note=collision lift
G1 X265.285934 Y310.370536 Z5.753761 E16906.203903 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.646324 matz1=5.753761 note=collision lift
G1 X265.283388 Y310.372425 Z5.752175 E16906.218641 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.753761 matz1=5.752175 note=collision lift
G1 X265.134203 Y310.483068 Z5.77101 E16906.994804 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.752175 matz1=5.77101 note=collision lift
G1 X265.123628 Y310.49091 Z5.777592 E16907.055998 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.77101 matz1=5.777592 note=collision lift
G1 X264.780486 Y310.745402 Z5.789257 E16908.832812 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.777592 matz1=5.789257 note=collision lift
G1 X264.770848 Y310.75255 Z5.783257 E16908.888592 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.789257 matz1=5.783257 note=collision lift
G1 X264.608915 Y310.872647 Z5.756074 E16909.734362 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.783257 matz1=5.756074 note=collision lift
G1 X264.592341 Y310.88494 Z5.745756 E16909.83028 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.756074 matz1=5.745756 note=collision lift
G1 X264.52313 Y310.93627 Z5.714964 E16910.210713 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.745756 matz1=5.714964 note=collision lift
G1 X263.454008 Y311.729185 Z5.049431 E16916.397833 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.714964 matz1=5.049431 note=collision lift
G1 X261.653753 Y312.808216 Z4 E16926.153861 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 matz0=5.049431 matz1=4 note=collision lift
G1 X261.497732 Y312.901732 Z4 E16926.910117 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X259.435946 Y313.876884 Z4 E16936.392431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X257.288506 Y314.64525 Z4 E16945.874744 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X255.076094 Y315.199431 Z4 E16955.357057 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X253.253743 Y315.469751 Z4 E16963.016413 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002
G1 X252.820016 Y315.534088 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X250.542 Y315.646 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
G1 X248.263984 Y315.534088 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0002 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0002
G0 X248.263984 Y315.534088 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0001 note=intra-page lift
G0 X243.537431 Y348.177569 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0001 note=intra-page XY
G0 X243.537431 Y348.177569 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0001 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0001
G1 X242.530093 Y347.066142 Z4 E16963.328227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X242.332185 Y346.847784 Z4 E16963.462784 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X241.614188 Y345.879678 Z4 E16964.263668 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X241.263084 Y345.406268 Z4 E16964.801898 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X240.794941 Y344.625219 Z4 E16965.822737 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X240.340424 Y343.866904 Z4 E16967.033753 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X240.077092 Y343.310135 Z4 E16968.005433 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X239.573091 Y342.244515 Z4 E16970.158352 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X239.464881 Y341.942088 Z4 E16970.811757 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.968475 Y340.554726 Z4 E16974.175692 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.962035 Y340.529017 Z4 E16974.241709 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.597565 Y339.07397 Z4 E16978.295287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.532399 Y338.813812 Z4 E16979.085775 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.351656 Y337.59534 Z4 E16982.972494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.269062 Y337.038537 Z4 E16984.8886 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.22308 Y336.102561 Z4 E16988.273328 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.181 Y335.246 Z4 E16991.584167 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.212521 Y334.604368 Z4 E16994.19779 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=prime ramp
G1 X238.269062 Y333.453463 Z4 E16998.988468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X238.532399 Y331.678188 Z4 E17006.449961 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X238.968475 Y329.937274 Z4 E17013.911453 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X239.573091 Y328.247485 Z4 E17021.372946 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X240.340424 Y326.625096 Z4 E17028.834438 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X241.263084 Y325.085732 Z4 E17036.295931 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X242.332185 Y323.644216 Z4 E17043.757423 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X243.537431 Y322.314431 Z4 E17051.218916 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X244.867216 Y321.109185 Z4 E17058.680408 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X246.308732 Y320.040084 Z4 E17066.1419 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X247.848096 Y319.117424 Z4 E17073.603393 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X249.470485 Y318.350091 Z4 E17081.064885 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X251.160274 Y317.745475 Z4 E17088.526378 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X252.901188 Y317.309399 Z4 E17095.98787 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X254.676463 Y317.046062 Z4 E17103.449363 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X256.469 Y316.958 Z4 E17110.910855 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X256.612019 Y316.965026 Z4 E17111.506177 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X258.261537 Y317.046062 Z4.825754 E17119.182789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4 matz1=4.825754 note=collision lift
G1 X260.036812 Y317.309399 Z5.723103 E17127.524991 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.825754 matz1=5.723103 note=collision lift
G1 X261.777726 Y317.745475 Z6.620453 E17135.867194 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.723103 matz1=6 note=collision lift
G1 X263.467515 Y318.350091 Z7.517803 E17144.209396 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X264.339317 Y318.762423 Z8 E17148.692138 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X265.089904 Y319.117424 Z8 E17152.144144 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X266.629268 Y320.040084 Z8 E17159.605636 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X267.794905 Y320.904579 Z8 E17165.639139 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X268.070784 Y321.109185 Z7.828264 E17167.23568 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X269.400569 Y322.314431 Z6.930915 E17175.577882 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X270.605815 Y323.644216 Z7.828264 E17183.920084 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X270.810421 Y323.920095 Z8 E17185.516625 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X271.674916 Y325.085732 Z8 E17191.550128 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X272.597576 Y326.625096 Z8 E17199.011621 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X272.952577 Y327.375683 Z8 E17202.463626 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X273.364909 Y328.247485 Z7.517803 E17206.946369 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X273.969525 Y329.937274 Z6.620453 E17215.288571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=6 note=collision lift
G1 X274.405601 Y331.678188 Z5.723103 E17223.630773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=6 matz1=5.723103 note=collision lift
G1 X274.668938 Y333.453463 Z4.825754 E17231.972975 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=5.723103 matz1=4.825754 note=collision lift
G1 X274.749974 Y335.102981 Z4 E17239.649588 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 matz0=4.825754 matz1=4 note=collision lift
G1 X274.757 Y335.246 Z4 E17240.244909 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X274.668938 Y337.038537 Z4 E17247.706402 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X274.405601 Y338.813812 Z4 E17255.167894 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X273.969525 Y340.554726 Z4 E17262.629387 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X273.364909 Y342.244515 Z4 E17270.090879 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X272.597576 Y343.866904 Z4 E17277.552372 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X271.674916 Y345.406268 Z4 E17285.013864 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X270.605815 Y346.847784 Z4 E17292.475356 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X269.400569 Y348.177569 Z4 E17299.936849 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X268.070784 Y349.382815 Z4 E17307.398341 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X266.629268 Y350.451916 Z4 E17314.859834 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X265.089904 Y351.374576 Z4 E17322.321326 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X263.467515 Y352.141909 Z4 E17329.782819 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X261.777726 Y352.746525 Z4 E17337.244311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X260.036812 Y353.182601 Z4 E17344.705804 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X258.261537 Y353.445938 Z4 E17352.167296 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X256.469 Y353.534 Z4 E17359.628789 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X254.676463 Y353.445938 Z4 E17367.090281 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X252.901188 Y353.182601 Z4 E17374.551773 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X251.160274 Y352.746525 Z4 E17382.013266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X249.470485 Y352.141909 Z4 E17389.474758 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X247.848096 Y351.374576 Z4 E17396.936251 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X247.518645 Y351.17711 Z4 E17398.533144 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001
G1 X246.308732 Y350.451916 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=end-early tail
G1 X244.867216 Y349.382815 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=end-early tail
G1 X243.537431 Y348.177569 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0001 note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=1 id=stroke-0001
G0 X243.537431 Y348.177569 Z8 F2400 ; clayline kind=travel_lift page=0 layer=1 stroke=stroke-0000 note=intra-page lift
G0 X231.683462 Y360.031538 Z8 F2400 ; clayline kind=travel_xy page=0 layer=1 stroke=stroke-0000 note=intra-page XY
G0 X231.683462 Y360.031538 Z4 F2400 ; clayline kind=travel_approach page=0 layer=1 stroke=stroke-0000 note=intra-page approach
; CLAYLINE_STROKE_BEGIN page=0 layer=1 id=stroke-0000
G1 X230.676124 Y358.920111 Z4 E17398.844957 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X229.925811 Y358.092269 Z4 E17399.482457 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X229.697819 Y357.784857 Z4 E17399.780399 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X228.80427 Y356.580046 Z4 E17401.339468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X228.366705 Y355.990058 Z4 E17402.330398 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X227.97318 Y355.333501 Z4 E17403.522164 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X227.202026 Y354.046908 Z4 E17406.328488 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X227.02116 Y353.745151 Z4 E17407.076967 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X226.530245 Y352.707199 Z4 E17409.758439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X225.902133 Y351.379167 Z4 E17413.722163 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X225.891716 Y351.350054 Z4 E17413.812018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X225.386381 Y349.937738 Z4 E17418.489225 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X225.020401 Y348.914892 Z4 E17422.265986 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X224.919892 Y348.513638 Z4 E17423.790059 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X224.555422 Y347.058591 Z4 E17429.71452 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=prime ramp
G1 X224.384457 Y346.376059 Z4 E17432.639826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.000423 Y343.787117 Z4 E17443.521169 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X223.872 Y341.173 Z4 E17454.402512 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.000423 Y338.558883 Z4 E17465.283856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X224.384457 Y335.969941 Z4 E17476.165199 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X225.020401 Y333.431108 Z4 E17487.046542 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X225.902133 Y330.966833 Z4 E17497.927885 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X227.02116 Y328.600849 Z4 E17508.809228 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X228.366705 Y326.355942 Z4 E17519.690571 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X229.925811 Y324.253731 Z4 E17530.571915 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X231.683462 Y322.314462 Z4 E17541.453258 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X233.622731 Y320.556811 Z4 E17552.334601 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X235.724942 Y318.997705 Z4 E17563.215944 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.969849 Y317.65216 Z4 E17574.097287 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X240.335833 Y316.533133 Z4 E17584.97863 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.800108 Y315.651401 Z4 E17595.859974 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.338941 Y315.015457 Z4 E17606.741317 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.927883 Y314.631423 Z4 E17617.62266 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.542 Y314.503 Z4 E17628.504003 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X252.359966 Y314.592311 Z4 E17636.071344 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.156117 Y314.631423 Z4.398555 E17639.776511 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4 matz1=4.398555 note=collision lift
G1 X255.745059 Y315.015457 Z5.70719 E17651.942223 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4.398555 matz1=5.70719 note=collision lift
G1 X258.283892 Y315.651401 Z7.015825 E17664.107934 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.70719 matz1=6 note=collision lift
G1 X259.62207 Y316.130209 Z7.726454 E17670.714292 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X259.626233 Y316.131699 Z7.724243 E17670.734847 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X260.273774 Y316.363392 Z7.84407 E17673.637227 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X260.274031 Y316.363484 Z7.843934 E17673.638494 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X260.747799 Y316.533001 Z7.930104 E17675.760936 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X260.748167 Y316.533133 Z7.9303 E17675.762754 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X261.096084 Y316.697685 Z8 E17677.388878 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X261.096517 Y316.69789 Z8 E17677.390871 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X263.114151 Y317.65216 Z8 E17686.670125 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X265.359058 Y318.997705 Z8 E17697.551468 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X267.461269 Y320.556811 Z8 E17708.432811 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X269.400538 Y322.314462 Z8 E17719.314155 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X271.158189 Y324.253731 Z8 E17730.195498 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X272.717295 Y326.355942 Z8 E17741.076841 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X274.06284 Y328.600849 Z8 E17751.958184 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X275.01711 Y330.618483 Z8 E17761.237439 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X275.017315 Y330.618916 Z8 E17761.239431 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X275.181867 Y330.966833 Z7.9303 E17762.865555 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X275.181999 Y330.967201 Z7.930104 E17762.867373 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X275.351516 Y331.440969 Z7.843934 E17764.989815 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X275.351608 Y331.441226 Z7.84407 E17764.991083 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X275.583301 Y332.088767 Z7.724243 E17767.893463 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X275.584791 Y332.09293 Z7.726454 E17767.914018 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X276.063599 Y333.431108 Z7.015825 E17774.520375 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=6 note=collision lift
G1 X276.699543 Y335.969941 Z5.70719 E17786.686087 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=6 matz1=5.70719 note=collision lift
G1 X277.083577 Y338.558883 Z4.398555 E17798.851798 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=5.70719 matz1=4.398555 note=collision lift
G1 X277.122689 Y339.355034 Z4 E17802.556965 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 matz0=4.398555 matz1=4 note=collision lift
G1 X277.212 Y341.173 Z4 E17810.124306 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X277.083577 Y343.787117 Z4 E17821.005649 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X276.699543 Y346.376059 Z4 E17831.886993 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X276.063599 Y348.914892 Z4 E17842.768336 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X275.181867 Y351.379167 Z4 E17853.649679 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X274.06284 Y353.745151 Z4 E17864.531022 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X272.717295 Y355.990058 Z4 E17875.412365 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X271.158189 Y358.092269 Z4 E17886.293708 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X269.400538 Y360.031538 Z4 E17897.175051 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X267.461269 Y361.789189 Z4 E17908.056395 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X265.359058 Y363.348295 Z4 E17918.937738 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X263.114151 Y364.69384 Z4 E17929.819081 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X260.748167 Y365.812867 Z4 E17940.700424 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X258.283892 Y366.694599 Z4 E17951.581767 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X255.745059 Y367.330543 Z4 E17962.46311 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X253.156117 Y367.714577 Z4 E17973.344454 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X250.542 Y367.843 Z4 E17984.225797 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X247.927883 Y367.714577 Z4 E17995.10714 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X245.338941 Y367.330543 Z4 E18005.988483 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X242.800108 Y366.694599 Z4 E18016.869826 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X240.335833 Y365.812867 Z4 E18027.751169 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X237.969849 Y364.69384 Z4 E18038.632513 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X235.724942 Y363.348295 Z4 E18049.513856 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X235.536558 Y363.20858 Z4 E18050.488958 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000
G1 X233.622731 Y361.789189 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
G1 X231.683462 Y360.031538 Z4 F2400 ; clayline kind=print page=0 layer=1 stroke=stroke-0000 note=end-early tail
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
