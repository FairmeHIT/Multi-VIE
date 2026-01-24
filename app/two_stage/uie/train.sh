
python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/00/model_best --train_path uie_file/data/00_data/train.txt --dev_path uie_file/data/00_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/00/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1


python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/01/model_best --train_path uie_file/data/01_data/train.txt --dev_path uie_file/data/01_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/01/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1


python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/02/model_best --train_path uie_file/data/02_data/train.txt --dev_path uie_file/data/02_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/02/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1


python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/03/model_best --train_path uie_file/data/03_data/train.txt --dev_path uie_file/data/03_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/03/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1


python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/04/model_best --train_path uie_file/data/04_data/train.txt --dev_path uie_file/data/04_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/04/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1



python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/05/model_best --train_path uie_file/data/05_data/train.txt --dev_path uie_file/data/05_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/05/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1



python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/06/model_best --train_path uie_file/data/06_data/train.txt --dev_path uie_file/data/06_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/06/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1



python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/07/model_best --train_path uie_file/data/07_data/train.txt --dev_path uie_file/data/07_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/07/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1



python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/08/model_best --train_path uie_file/data/08_data/train.txt --dev_path uie_file/data/08_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/08/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1



python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/09/model_best --train_path uie_file/data/09_data/train.txt --dev_path uie_file/data/09_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/09/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1




python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/10/model_best --train_path uie_file/data/10_data/train.txt --dev_path uie_file/data/10_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/10/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1



python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/11/model_best --train_path uie_file/data/11_data/train.txt --dev_path uie_file/data/11_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/11/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1



python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/12/model_best --train_path uie_file/data/12_data/train.txt --dev_path uie_file/data/12_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/12/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1



python -u -m paddle.distributed.launch --gpus "0" finetune.py --device gpu --logging_steps 10 --save_steps 100 --eval_steps 100 --seed 42 --model_name_or_path uie_file/uie_base/ --output_dir uie_file/checkpoint/13/model_best --train_path uie_file/data/13_data/train.txt --dev_path uie_file/data/13_data/dev.txt --max_seq_length 512 --per_device_eval_batch_size 16 --per_device_train_batch_size 16 --num_train_epochs 100 --learning_rate 1e-5 --do_train --do_eval --do_export --export_model_dir uie_file/checkpoint/13/model_best --label_names "start_positions" "end_positions" --overwrite_output_dir --disable_tqdm True --metric_for_best_model eval_f1 --load_best_model_at_end True --save_total_limit 1