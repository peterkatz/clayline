; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=calibration-kiss-pair
; prepared_trace_sha256=c89818a005bbdd3292bfb204066413d3bd0d39b3573ed35b7d82eec89871fcd4
; body_sha256=5fd936cebaf8549bf0edfa4ea8164c519d8e2ab6841eaf086827e9e2606d0836
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
; stats.motion_count=219
; stats.print_motion_count=214
; stats.travel_motion_count=5
; stats.stroke_count=2
; stats.page_count=1
; stats.print_path_mm=502.565112
; stats.deposited_path_mm=492.565112
; stats.travel_path_mm=108.125
; stats.total_motion_path_mm=610.690112
; stats.motion_time_seconds=19.455295
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=19.455295
; stats.body_volume_mm3=3581.738341
; stats.wet_weight_g=6.447129
; stats.body_e=1489.113762
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=calibration-kiss-pair calibration
; parameter.calibration=kiss-pair
; parameter.center_spacing_mm=83.75
; parameter.circle_segments=96
; parameter.nozzle_diameter_mm=5
; parameter.overlap_fraction=0.25
; parameter.ring_diameter_mm=80
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
; CLAYLINE_MARKER page=0 layer=0 text=KISS PAIR left
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=kiss-left
G0 X205.625 Y202.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=kiss-left note=stroke start XY at safe Z
G0 X205.625 Y202.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=kiss-left note=stroke start vertical approach
G1 X205.575921 Y203.999197 Z1.5 E0.23386 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X205.539357 Y205.116125 Z1.5 E0.712125 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=KISS PAIR left
G1 X205.501868 Y205.496757 Z1.5 E0.935441 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X205.354842 Y206.989534 Z1.5 E2.104743 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X205.282794 Y207.721048 Z1.5 E2.8485 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X205.158188 Y208.475777 Z1.5 E3.741765 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X204.913845 Y209.955742 Z1.5 E5.846508 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X204.856411 Y210.303613 Z1.5 E6.409125 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X204.595859 Y211.421059 Z1.5 E8.418972 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X204.262033 Y212.852762 Z1.5 E11.394 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X204.253355 Y212.881368 Z1.5 E11.459156 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X203.817928 Y214.316779 Z1.5 E14.967061 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X203.502205 Y215.357579 Z1.5 E17.803126 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X203.356949 Y215.743515 Z1.5 E18.942686 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X202.828574 Y217.147374 Z1.5 E23.386032 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=prime ramp
G1 X202.580181 Y217.807337 Z1.5 E25.584818 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X201.49991 Y220.191548 Z1.5 E33.746626 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X200.266016 Y222.5 Z1.5 E41.908434 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X198.883784 Y224.722809 Z1.5 E50.070243 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X197.359134 Y226.850457 Z1.5 E58.232051 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X195.698592 Y228.873833 Z1.5 E66.393859 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X193.909271 Y230.784271 Z1.5 E74.555668 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X191.998833 Y232.573592 Z1.5 E82.717476 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X189.975457 Y234.234134 Z1.5 E90.879284 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X187.847809 Y235.758784 Z1.5 E99.041093 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X185.625 Y237.141016 Z1.5 E107.202901 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X183.316548 Y238.37491 Z1.5 E115.364709 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X180.932337 Y239.455181 Z1.5 E123.526518 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X178.482579 Y240.377205 Z1.5 E131.688326 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X175.977762 Y241.137033 Z1.5 E139.850135 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X173.428613 Y241.731411 Z1.5 E148.011943 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X170.846048 Y242.157794 Z1.5 E156.173751 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X168.241125 Y242.414357 Z1.5 E164.33556 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X165.625 Y242.5 Z1.5 E172.497368 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X163.008875 Y242.414357 Z1.5 E180.659176 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X160.403952 Y242.157794 Z1.5 E188.820985 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X157.821387 Y241.731411 Z1.5 E196.982793 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X155.272238 Y241.137033 Z1.5 E205.144601 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X152.767421 Y240.377205 Z1.5 E213.30641 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X150.317663 Y239.455181 Z1.5 E221.468218 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X147.933452 Y238.37491 Z1.5 E229.630026 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X145.625 Y237.141016 Z1.5 E237.791835 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X143.402191 Y235.758784 Z1.5 E245.953643 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X141.274543 Y234.234134 Z1.5 E254.115451 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X139.251167 Y232.573592 Z1.5 E262.27726 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X137.340729 Y230.784271 Z1.5 E270.439068 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X135.551408 Y228.873833 Z1.5 E278.600876 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X133.890866 Y226.850457 Z1.5 E286.762685 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X132.366216 Y224.722809 Z1.5 E294.924493 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X130.983984 Y222.5 Z1.5 E303.086302 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X129.75009 Y220.191548 Z1.5 E311.24811 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X128.669819 Y217.807337 Z1.5 E319.409918 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X127.747795 Y215.357579 Z1.5 E327.571727 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X126.987967 Y212.852762 Z1.5 E335.733535 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X126.393589 Y210.303613 Z1.5 E343.895343 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X125.967206 Y207.721048 Z1.5 E352.057152 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X125.710643 Y205.116125 Z1.5 E360.21896 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X125.625 Y202.5 Z1.5 E368.380768 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X125.710643 Y199.883875 Z1.5 E376.542577 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X125.967206 Y197.278952 Z1.5 E384.704385 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X126.393589 Y194.696387 Z1.5 E392.866193 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X126.987967 Y192.147238 Z1.5 E401.028002 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X127.747795 Y189.642421 Z1.5 E409.18981 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X128.669819 Y187.192663 Z1.5 E417.351618 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X129.75009 Y184.808452 Z1.5 E425.513427 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X130.983984 Y182.5 Z1.5 E433.675235 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X132.366216 Y180.277191 Z1.5 E441.837043 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X133.890866 Y178.149543 Z1.5 E449.998852 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X135.551408 Y176.126167 Z1.5 E458.16066 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X137.340729 Y174.215729 Z1.5 E466.322469 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X139.251167 Y172.426408 Z1.5 E474.484277 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X141.274543 Y170.765866 Z1.5 E482.646085 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X143.402191 Y169.241216 Z1.5 E490.807894 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X145.625 Y167.858984 Z1.5 E498.969702 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X147.933452 Y166.62509 Z1.5 E507.13151 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X150.317663 Y165.544819 Z1.5 E515.293319 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X152.767421 Y164.622795 Z1.5 E523.455127 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X155.272238 Y163.862967 Z1.5 E531.616935 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X157.821387 Y163.268589 Z1.5 E539.778744 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X160.403952 Y162.842206 Z1.5 E547.940552 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X163.008875 Y162.585643 Z1.5 E556.10236 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X165.625 Y162.5 Z1.5 E564.264169 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X168.241125 Y162.585643 Z1.5 E572.425977 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X170.846048 Y162.842206 Z1.5 E580.587785 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X173.428613 Y163.268589 Z1.5 E588.749594 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X175.977762 Y163.862967 Z1.5 E596.911402 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X178.482579 Y164.622795 Z1.5 E605.07321 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X180.932337 Y165.544819 Z1.5 E613.235019 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X183.316548 Y166.62509 Z1.5 E621.396827 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X185.625 Y167.858984 Z1.5 E629.558635 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X187.847809 Y169.241216 Z1.5 E637.720444 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X189.975457 Y170.765866 Z1.5 E645.882252 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X191.998833 Y172.426408 Z1.5 E654.044061 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X193.909271 Y174.215729 Z1.5 E662.205869 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X195.698592 Y176.126167 Z1.5 E670.367677 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X197.359134 Y178.149543 Z1.5 E678.529486 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X198.883784 Y180.277191 Z1.5 E686.691294 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X200.266016 Y182.5 Z1.5 E694.853102 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X201.49991 Y184.808452 Z1.5 E703.014911 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X202.580181 Y187.192663 Z1.5 E711.176719 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X203.502205 Y189.642421 Z1.5 E719.338527 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X204.262033 Y192.147238 Z1.5 E727.500336 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X204.856411 Y194.696387 Z1.5 E735.662144 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X205.282794 Y197.278952 Z1.5 E743.823952 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X205.305834 Y197.512874 Z1.5 E744.556881 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left
G1 X205.539357 Y199.883875 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=end-early tail
G1 X205.625 Y202.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-left note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=kiss-left
; CLAYLINE_MARKER page=0 layer=0 text=KISS PAIR right
G0 X205.625 Y202.5 Z3.5 F2400 ; clayline kind=travel_lift page=0 layer=0 stroke=none
G0 X289.375 Y202.5 Z3.5 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=none
G0 X289.375 Y202.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=none
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=kiss-right
G1 X289.325921 Y203.999197 Z1.5 E744.790741 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X289.289357 Y205.116125 Z1.5 E745.269006 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=KISS PAIR right
G1 X289.251868 Y205.496757 Z1.5 E745.492322 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X289.104842 Y206.989534 Z1.5 E746.661624 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X289.032794 Y207.721048 Z1.5 E747.405381 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X288.908188 Y208.475777 Z1.5 E748.298646 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X288.663845 Y209.955742 Z1.5 E750.403389 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X288.606411 Y210.303613 Z1.5 E750.966006 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X288.345859 Y211.421059 Z1.5 E752.975852 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X288.012033 Y212.852762 Z1.5 E755.950881 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X288.003355 Y212.881368 Z1.5 E756.016037 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X287.567928 Y214.316779 Z1.5 E759.523942 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X287.252205 Y215.357579 Z1.5 E762.360006 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X287.106949 Y215.743515 Z1.5 E763.499567 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X286.578574 Y217.147374 Z1.5 E767.942913 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=prime ramp
G1 X286.330181 Y217.807337 Z1.5 E770.141698 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X285.24991 Y220.191548 Z1.5 E778.303507 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X284.016016 Y222.5 Z1.5 E786.465315 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X282.633784 Y224.722809 Z1.5 E794.627123 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X281.109134 Y226.850457 Z1.5 E802.788932 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X279.448592 Y228.873833 Z1.5 E810.95074 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X277.659271 Y230.784271 Z1.5 E819.112549 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X275.748833 Y232.573592 Z1.5 E827.274357 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X273.725457 Y234.234134 Z1.5 E835.436165 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X271.597809 Y235.758784 Z1.5 E843.597974 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X269.375 Y237.141016 Z1.5 E851.759782 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X267.066548 Y238.37491 Z1.5 E859.92159 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X264.682337 Y239.455181 Z1.5 E868.083399 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X262.232579 Y240.377205 Z1.5 E876.245207 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X259.727762 Y241.137033 Z1.5 E884.407015 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X257.178613 Y241.731411 Z1.5 E892.568824 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X254.596048 Y242.157794 Z1.5 E900.730632 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X251.991125 Y242.414357 Z1.5 E908.89244 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X249.375 Y242.5 Z1.5 E917.054249 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X246.758875 Y242.414357 Z1.5 E925.216057 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X244.153952 Y242.157794 Z1.5 E933.377865 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X241.571387 Y241.731411 Z1.5 E941.539674 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X239.022238 Y241.137033 Z1.5 E949.701482 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X236.517421 Y240.377205 Z1.5 E957.86329 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X234.067663 Y239.455181 Z1.5 E966.025099 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X231.683452 Y238.37491 Z1.5 E974.186907 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X229.375 Y237.141016 Z1.5 E982.348715 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X227.152191 Y235.758784 Z1.5 E990.510524 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X225.024543 Y234.234134 Z1.5 E998.672332 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X223.001167 Y232.573592 Z1.5 E1006.834141 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X221.090729 Y230.784271 Z1.5 E1014.995949 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X219.301408 Y228.873833 Z1.5 E1023.157757 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X217.640866 Y226.850457 Z1.5 E1031.319566 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X216.116216 Y224.722809 Z1.5 E1039.481374 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X214.733984 Y222.5 Z1.5 E1047.643182 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X213.50009 Y220.191548 Z1.5 E1055.804991 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X212.419819 Y217.807337 Z1.5 E1063.966799 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X211.497795 Y215.357579 Z1.5 E1072.128607 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X210.737967 Y212.852762 Z1.5 E1080.290416 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X210.143589 Y210.303613 Z1.5 E1088.452224 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X209.717206 Y207.721048 Z1.5 E1096.614032 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X209.460643 Y205.116125 Z1.5 E1104.775841 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X209.375 Y202.5 Z1.5 E1112.937649 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X209.460643 Y199.883875 Z1.5 E1121.099457 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X209.717206 Y197.278952 Z1.5 E1129.261266 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X210.143589 Y194.696387 Z1.5 E1137.423074 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X210.737967 Y192.147238 Z1.5 E1145.584882 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X211.497795 Y189.642421 Z1.5 E1153.746691 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X212.419819 Y187.192663 Z1.5 E1161.908499 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X213.50009 Y184.808452 Z1.5 E1170.070308 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X214.733984 Y182.5 Z1.5 E1178.232116 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X216.116216 Y180.277191 Z1.5 E1186.393924 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X217.640866 Y178.149543 Z1.5 E1194.555733 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X219.301408 Y176.126167 Z1.5 E1202.717541 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X221.090729 Y174.215729 Z1.5 E1210.879349 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X223.001167 Y172.426408 Z1.5 E1219.041158 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X225.024543 Y170.765866 Z1.5 E1227.202966 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X227.152191 Y169.241216 Z1.5 E1235.364774 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X229.375 Y167.858984 Z1.5 E1243.526583 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X231.683452 Y166.62509 Z1.5 E1251.688391 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X234.067663 Y165.544819 Z1.5 E1259.850199 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X236.517421 Y164.622795 Z1.5 E1268.012008 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X239.022238 Y163.862967 Z1.5 E1276.173816 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X241.571387 Y163.268589 Z1.5 E1284.335624 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X244.153952 Y162.842206 Z1.5 E1292.497433 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X246.758875 Y162.585643 Z1.5 E1300.659241 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X249.375 Y162.5 Z1.5 E1308.821049 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X251.991125 Y162.585643 Z1.5 E1316.982858 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X254.596048 Y162.842206 Z1.5 E1325.144666 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X257.178613 Y163.268589 Z1.5 E1333.306475 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X259.727762 Y163.862967 Z1.5 E1341.468283 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X262.232579 Y164.622795 Z1.5 E1349.630091 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X264.682337 Y165.544819 Z1.5 E1357.7919 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X267.066548 Y166.62509 Z1.5 E1365.953708 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X269.375 Y167.858984 Z1.5 E1374.115516 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X271.597809 Y169.241216 Z1.5 E1382.277325 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X273.725457 Y170.765866 Z1.5 E1390.439133 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X275.748833 Y172.426408 Z1.5 E1398.600941 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X277.659271 Y174.215729 Z1.5 E1406.76275 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X279.448592 Y176.126167 Z1.5 E1414.924558 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X281.109134 Y178.149543 Z1.5 E1423.086366 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X282.633784 Y180.277191 Z1.5 E1431.248175 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X284.016016 Y182.5 Z1.5 E1439.409983 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X285.24991 Y184.808452 Z1.5 E1447.571791 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X286.330181 Y187.192663 Z1.5 E1455.7336 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X287.252205 Y189.642421 Z1.5 E1463.895408 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X288.012033 Y192.147238 Z1.5 E1472.057216 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X288.606411 Y194.696387 Z1.5 E1480.219025 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X289.032794 Y197.278952 Z1.5 E1488.380833 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X289.055834 Y197.512874 Z1.5 E1489.113762 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right
G1 X289.289357 Y199.883875 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=end-early tail
G1 X289.375 Y202.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=kiss-right note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=kiss-right
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
