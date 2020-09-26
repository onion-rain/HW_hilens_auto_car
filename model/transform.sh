MODEL_NAME=yolo3_darknet53.pb
MODEL_CFG=insert_op_conf.cfg
OUTPUT_NAME=yolo3_darknet53_raw3_4_sup_slope_now_terminal_t

MODEL_INPUT='images:1,416,416,3'

/opt/ddk/bin/aarch64-linux-gcc7.3.0/omg --model=$MODEL_NAME --input_shape=$MODEL_INPUT --framework=3 --output=$OUTPUT_NAME --insert_op_conf=$MODEL_CFG
