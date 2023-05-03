# Training

The pipeline of our method can roughly be summarized as follows:

0. **Remeshing:** the mesh templates of each category (potentally hand-modeled) are remeshed into a common topology by deforming a sphere template.
1. **Silhouette optimization (step 1/2 of pose estimation):** we estimate pose hypotheses for each image by fitting the mesh templates to the object mask.
2. **Semantic template inference and ambiguity resolution (step 2/2 of pose estimation):** using part semantics, we learn a semantic template for each mesh template and use it for resolving ambiguous views (e.g. front-back confusion).
3. **Mesh estimation:** we learn a reconstruction model in order to estimate a 3D mesh for each image.
4. **Pseudo-ground-truth dataset:** we convert the dataset from image space to UV space (displacement maps + partial textures).
5. **GAN training:** we learn a GAN in UV space trained on the pseudo-ground-truth dataset.

## Generating pseudo-ground-truth data
If your goal is to train the GAN without running the entire pipeline from scratch, you can follow this section and the next one.
This step requires a trained mesh estimation model. You can use the pretrained one we provide or train it from scratch as described in one of the next sections.
The pseudo-ground-truth for a dataset can be generated by specifying the `--generate_pseudogt` flag in `run_reconstruction.py`:
```
python run_reconstruction.py --name pretrained_p3d_car_singletpl --dataset p3d_car --batch_size 10 --generate_pseudogt --num_workers 1
python run_reconstruction.py --name pretrained_p3d_airplane_singletpl --dataset p3d_airplane --batch_size 10 --generate_pseudogt --num_workers 1

python run_reconstruction.py --name pretrained_cub_singletpl --dataset cub --batch_size 10 --generate_pseudogt --num_workers 1

python run_reconstruction.py --name pretrained_imagenet_motorcycle_singletpl --dataset imagenet_motorcycle --batch_size 10 --generate_pseudogt --num_workers 1
[repeat for the other ImageNet classes]

python run_reconstruction.py --name pretrained_all_singletpl --dataset all --batch_size 10 --generate_pseudogt --num_workers 1
```
For the other ImageNet classes, it suffices to replace `motorcycle` with the name of the class. The type of setting (single-template or multi-template) is autodetected from the experiment name (`_singletpl` or `_multitpl`) but can also be specified manually using `--mode`. 


## GAN training
To train the mesh generator, you first need to set up the pseudo-ground-truth data as described in the section above. Then, you can train a new model as follows:

- Pascal3D+ Car and Airplane
```
python run_generation.py --name new_p3d_car_singletpl --dataset p3d_car --gpu_ids 0,1,2,3 --batch_size 32 --num_discriminators 2 --iters 100000 --tensorboard
python run_generation.py --name new_p3d_airplane_singletpl --dataset p3d_airplane --gpu_ids 0,1,2,3 --batch_size 32 --num_discriminators 2 --iters 100000 --tensorboard
```

- CUB Birds
```
python run_generation.py --name new_cub_singletpl --dataset cub --gpu_ids 0,1,2,3 --batch_size 32 --num_discriminators 3 --epochs 800 --tensorboard
```

- ImageNet (for the other classes, just replace `motorcycle` with the class name)
```
python run_generation.py --name new_imagenet_motorcycle_singletpl --dataset imagenet_motorcycle --gpu_ids 0,1,2,3 --batch_size 32 --num_discriminators 3 --iters 80000 --tensorboard
```

- Conditional model trained to generate all classes (setting B)
```
python run_generation.py --name new_all_singletpl --dataset all --conditional_class --gpu_ids 0,1,2,3,4,5,6,7 --batch_size 64 --num_discriminators 3 --epochs 400 --tensorboard
```

These commands refer to the single-template setting. For the multi-template setting, simply replace `singletpl` with `multitpl`. You can specify the duration of the training run either through `--epochs` or `--iters`. The latter is easier to tune when working with datasets of different size. If you specify `--tensorboard`, training curves, FID curves, and generated results will be exported in the Tensorboard log directory `tensorboard_gan`. Note that using a different batch size or number of GPUs might results in slightly different results than those reported in the paper.

Once the training process has finished, you can find the best checkpoint (in terms of FID score) by specifying `--evaluate --which_epoch best`, e.g.
```
python run_generation.py --name new_cub_singletpl --dataset cub --gpu_ids 0,1,2,3 --batch_size 64 --evaluate --which_epoch best
```

## Mesh estimation model training
This step requires estimated poses from our pose estimation pipeline. For the datasets we use, these are already provided in the cache directory, but you are free to recompute them by following the instructions in the *Pose estimation* section (also needed if you use a custom dataset).

To train the mesh estimation model, you can use the following commands:
```
python run_reconstruction.py --name new_p3d_car_singletpl --dataset p3d_car --gpu_ids 0 --iters 130000 --tensorboard
python run_reconstruction.py --name new_p3d_airplane_singletpl --dataset p3d_airplane --gpu_ids 0 --iters 130000 --tensorboard

python run_reconstruction.py --name new_cub_singletpl --dataset cub --batch_size 10 --gpu_ids 0 --tensorboard

python run_reconstruction.py --name new_imagenet_motorcycle_singletpl --dataset imagenet_motorcycle --gpu_ids 0 --iters 130000 --tensorboard
[repeat for the other ImageNet classes]

python run_reconstruction.py --name pretrained_all_singletpl --dataset all --batch_size 128  --gpu_ids 0,1,2,3 --tensorboard
```
These commands refer to the single-template setting. For the multi-template setting, simply replace `singletpl` with `multitpl`. You can specify the duration of the training run either through `--epochs` or `--iters`. Tensorboard logs are saved in `tensorboard_recon`. By default, the scripts preloads the entire dataset into memory to speed up training; if you run into system memory errors, you can disable this feature by specifying `--no_prefetch`.

## Pose estimation
The two steps of the pose estimation approach (silhouette fitting & semantics) are handled by two separate scripts: `pose_optimization_step1.py` and `pose_optimization_step2.py`. Here are some examples:
```
python pose_optimization_step1.py --dataset p3d_car --mode singletpl --gpu_ids 0,1,2,3,4,5,6,7
python pose_optimization_step2.py --dataset p3d_car --mode singletpl --gpu_ids 0,1,2,3,4,5,6,7

python pose_optimization_step1.py --dataset cub --mode singletpl --gpu_ids 0,1,2,3,4,5,6,7
python pose_optimization_step2.py --dataset cub --mode singletpl --gpu_ids 0,1,2,3,4,5,6,7

python pose_optimization_step1.py --dataset imagenet_motorcycle --mode singletpl --gpu_ids 0,1,2,3,4,5,6,7
python pose_optimization_step2.py --dataset imagenet_motorcycle --mode singletpl --gpu_ids 0,1,2,3,4,5,6,7
```
By default, the total batch size is automatically tuned according to the number of specified GPUs. It is recommended to use all available GPUs for performance reasons (the result is not affected by the number of GPUs or batch size). The mode `singletpl` or `multitpl` must be specified explicitly using `--mode`.

## Remeshing
This is a pre-processing step that simplifies a hand-modeled mesh (potentially high-poly) to a common topology by deforming a sphere template. It has the purpose of enabling efficient batching and reducing the computational cost associated with rendering. All the mesh templates used in this work have already been remeshed and saved under `cache/remeshed_templates/`, whereas the originals can be found in `mesh_templates/classes/`. If you wish to repeat the procedure yourself, e.g. because you are incorporating a new mesh template for a new dataset, you can run:

```
python remesh.py --mode singletpl --gpu_ids 0,1,2,3,4,5,6,7 [--classes all]
```
The setting `singletpl` or `multitpl` must be specified explicitly through `--mode`. It is recommended to use all available GPUs for performance reasons. By default, the script converts all available mesh templates, but you can also specify the categories manually with `--classes` (comma-separated).
