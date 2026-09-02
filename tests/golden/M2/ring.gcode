; CLAYLINE_HEADER_BEGIN
; clayline_version=0.1.0.dev0
; generated_utc=reproducible
; job_id=calibration-ring
; prepared_trace_sha256=7c71ec47a47b660e9e6e2053a993b03f5d5ebe02144900cc354ae64a1975da15
; body_sha256=d225c63c06875f0f0acb968485cd105bd32182967b32f48e4b8c8f0a6ffd8ec7
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
; stats.motion_count=109
; stats.print_motion_count=107
; stats.travel_motion_count=2
; stats.stroke_count=1
; stats.page_count=1
; stats.print_path_mm=251.282556
; stats.deposited_path_mm=246.282556
; stats.travel_path_mm=58.5
; stats.total_motion_path_mm=309.782556
; stats.motion_time_seconds=9.838585
; stats.pause_time_seconds=0
; stats.pressure_time_seconds=0
; stats.estimated_print_time_seconds=9.838585
; stats.body_volume_mm3=1790.869171
; stats.wet_weight_g=3.223565
; stats.body_e=744.556881
; stats.pressure_e_excluded=0
; stats.warning_count=0
; nominal_label=calibration-ring calibration
; parameter.calibration=ring
; parameter.circle_segments=96
; parameter.nozzle_diameter_mm=5
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
; CLAYLINE_MARKER page=0 layer=0 text=RING diameter=80mm
; CLAYLINE_STROKE_BEGIN page=0 layer=0 id=ring
G0 X247.5 Y202.5 Z20 F2400 ; clayline kind=travel_xy page=0 layer=0 stroke=ring note=stroke start XY at safe Z
G0 X247.5 Y202.5 Z1.5 F2400 ; clayline kind=travel_approach page=0 layer=0 stroke=ring note=stroke start vertical approach
G1 X247.450921 Y203.999197 Z1.5 E0.23386 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X247.414357 Y205.116125 Z1.5 E0.712125 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=RING diameter=80mm
G1 X247.376868 Y205.496757 Z1.5 E0.935441 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X247.229842 Y206.989534 Z1.5 E2.104743 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X247.157794 Y207.721048 Z1.5 E2.8485 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X247.033188 Y208.475777 Z1.5 E3.741765 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X246.788845 Y209.955742 Z1.5 E5.846508 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X246.731411 Y210.303613 Z1.5 E6.409125 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X246.470859 Y211.421059 Z1.5 E8.418972 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X246.137033 Y212.852762 Z1.5 E11.394 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X246.128355 Y212.881368 Z1.5 E11.459156 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X245.692928 Y214.316779 Z1.5 E14.967061 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X245.377205 Y215.357579 Z1.5 E17.803126 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X245.231949 Y215.743515 Z1.5 E18.942686 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X244.703574 Y217.147374 Z1.5 E23.386032 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=prime ramp
G1 X244.455181 Y217.807337 Z1.5 E25.584818 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X243.37491 Y220.191548 Z1.5 E33.746626 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X242.141016 Y222.5 Z1.5 E41.908434 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X240.758784 Y224.722809 Z1.5 E50.070243 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X239.234134 Y226.850457 Z1.5 E58.232051 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X237.573592 Y228.873833 Z1.5 E66.393859 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X235.784271 Y230.784271 Z1.5 E74.555668 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X233.873833 Y232.573592 Z1.5 E82.717476 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X231.850457 Y234.234134 Z1.5 E90.879284 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X229.722809 Y235.758784 Z1.5 E99.041093 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X227.5 Y237.141016 Z1.5 E107.202901 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X225.191548 Y238.37491 Z1.5 E115.364709 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X222.807337 Y239.455181 Z1.5 E123.526518 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X220.357579 Y240.377205 Z1.5 E131.688326 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X217.852762 Y241.137033 Z1.5 E139.850135 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X215.303613 Y241.731411 Z1.5 E148.011943 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X212.721048 Y242.157794 Z1.5 E156.173751 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X210.116125 Y242.414357 Z1.5 E164.33556 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X207.5 Y242.5 Z1.5 E172.497368 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X204.883875 Y242.414357 Z1.5 E180.659176 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X202.278952 Y242.157794 Z1.5 E188.820985 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X199.696387 Y241.731411 Z1.5 E196.982793 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X197.147238 Y241.137033 Z1.5 E205.144601 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X194.642421 Y240.377205 Z1.5 E213.30641 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X192.192663 Y239.455181 Z1.5 E221.468218 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X189.808452 Y238.37491 Z1.5 E229.630026 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X187.5 Y237.141016 Z1.5 E237.791835 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X185.277191 Y235.758784 Z1.5 E245.953643 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X183.149543 Y234.234134 Z1.5 E254.115451 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X181.126167 Y232.573592 Z1.5 E262.27726 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X179.215729 Y230.784271 Z1.5 E270.439068 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X177.426408 Y228.873833 Z1.5 E278.600876 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X175.765866 Y226.850457 Z1.5 E286.762685 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X174.241216 Y224.722809 Z1.5 E294.924493 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X172.858984 Y222.5 Z1.5 E303.086302 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X171.62509 Y220.191548 Z1.5 E311.24811 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X170.544819 Y217.807337 Z1.5 E319.409918 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X169.622795 Y215.357579 Z1.5 E327.571727 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X168.862967 Y212.852762 Z1.5 E335.733535 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X168.268589 Y210.303613 Z1.5 E343.895343 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X167.842206 Y207.721048 Z1.5 E352.057152 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X167.585643 Y205.116125 Z1.5 E360.21896 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X167.5 Y202.5 Z1.5 E368.380768 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X167.585643 Y199.883875 Z1.5 E376.542577 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X167.842206 Y197.278952 Z1.5 E384.704385 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X168.268589 Y194.696387 Z1.5 E392.866193 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X168.862967 Y192.147238 Z1.5 E401.028002 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X169.622795 Y189.642421 Z1.5 E409.18981 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X170.544819 Y187.192663 Z1.5 E417.351618 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X171.62509 Y184.808452 Z1.5 E425.513427 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X172.858984 Y182.5 Z1.5 E433.675235 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X174.241216 Y180.277191 Z1.5 E441.837043 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X175.765866 Y178.149543 Z1.5 E449.998852 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X177.426408 Y176.126167 Z1.5 E458.16066 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X179.215729 Y174.215729 Z1.5 E466.322469 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X181.126167 Y172.426408 Z1.5 E474.484277 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X183.149543 Y170.765866 Z1.5 E482.646085 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X185.277191 Y169.241216 Z1.5 E490.807894 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X187.5 Y167.858984 Z1.5 E498.969702 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X189.808452 Y166.62509 Z1.5 E507.13151 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X192.192663 Y165.544819 Z1.5 E515.293319 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X194.642421 Y164.622795 Z1.5 E523.455127 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X197.147238 Y163.862967 Z1.5 E531.616935 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X199.696387 Y163.268589 Z1.5 E539.778744 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X202.278952 Y162.842206 Z1.5 E547.940552 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X204.883875 Y162.585643 Z1.5 E556.10236 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X207.5 Y162.5 Z1.5 E564.264169 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X210.116125 Y162.585643 Z1.5 E572.425977 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X212.721048 Y162.842206 Z1.5 E580.587785 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X215.303613 Y163.268589 Z1.5 E588.749594 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X217.852762 Y163.862967 Z1.5 E596.911402 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X220.357579 Y164.622795 Z1.5 E605.07321 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X222.807337 Y165.544819 Z1.5 E613.235019 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X225.191548 Y166.62509 Z1.5 E621.396827 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X227.5 Y167.858984 Z1.5 E629.558635 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X229.722809 Y169.241216 Z1.5 E637.720444 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X231.850457 Y170.765866 Z1.5 E645.882252 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X233.873833 Y172.426408 Z1.5 E654.044061 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X235.784271 Y174.215729 Z1.5 E662.205869 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X237.573592 Y176.126167 Z1.5 E670.367677 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X239.234134 Y178.149543 Z1.5 E678.529486 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X240.758784 Y180.277191 Z1.5 E686.691294 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X242.141016 Y182.5 Z1.5 E694.853102 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X243.37491 Y184.808452 Z1.5 E703.014911 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X244.455181 Y187.192663 Z1.5 E711.176719 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X245.377205 Y189.642421 Z1.5 E719.338527 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X246.137033 Y192.147238 Z1.5 E727.500336 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X246.731411 Y194.696387 Z1.5 E735.662144 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X247.157794 Y197.278952 Z1.5 E743.823952 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X247.180834 Y197.512874 Z1.5 E744.556881 F1800 ; clayline kind=print page=0 layer=0 stroke=ring
G1 X247.414357 Y199.883875 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=end-early tail
G1 X247.5 Y202.5 Z1.5 F1800 ; clayline kind=print page=0 layer=0 stroke=ring note=end-early tail
; CLAYLINE_STROKE_END page=0 layer=0 id=ring
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
