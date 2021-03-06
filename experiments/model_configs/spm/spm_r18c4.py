from experiments.data_configs.got10k_lasot_trackingnet_coco import get_data_config

data_root = 'data/TrackingImageZips'
work_dir = './output/spm/spm_r18c4/'
log_level = 'INFO'
cudnn_benchmark = True
model = dict(
    type='SPM',
    backbone=dict(
        type='ResNet',
        depth=18,
        num_stages=4,
        strides=(1, 2, 1),
        dilations=(1, 1, 1),
        stem_padding=0,
        norm_eval=True,
        pretrained='data/pretrained_models/resnet18.pth',
        init_type='xavier_uniform',
    ),
    cm_fusion=dict(
        type='CrossCorrelation',
        feat_name='conv4',
        in_channels=256,
        corr_channels=256,
        out_channels=[10, 20],
        depth_wise=False,
        pre_kernel_size=3,
        init_type='xavier_uniform'
    ),
    cm_head=dict(
        type='RPNHead',
        stride=8,
        anchor_scales=(8.0, ),
        anchor_ratios=(0.33, 0.5, 1.0, 2.0, 3.0),
        target_means=(0.0, 0.0, 0.0, 0.0),
        target_stds=(1.0, 1.0, 1.0, 1.0),
        pre_convs=None,
        head_convs=[
            dict(num_layers=1, in_channels=10, out_channels=10, kernel_size=1, nonlinear_last=False),
            dict(num_layers=1, in_channels=20, out_channels=20, kernel_size=1, nonlinear_last=False),
        ],
        cls_loss=dict(type='CrossEntropyLoss', loss_weight=1.0),
        reg_loss=dict(type='L1Loss', loss_weight=1.0),
        init_type='xavier_uniform'
    ),
    fm_fusion=dict(
        type='BoxAlign',
        feat_name=['conv3', 'conv4'],
        in_channels=[128, 256],
        stride=[8, 8],
        out_size=6,
        post_convs=dict(num_layers=1, in_channels=(128 + 256) * 2, out_channels=256, kernel_size=1,
                        nonlinear_last=True),
        fuse_type='concat',
    ),
    fm_head=dict(
        type='CompareHead',
        in_channels=256,
        in_size=6,
        target_means=(0., 0., 0., 0.),
        target_stds=(0.1, 0.1, 0.1, 0.1),
        num_fcs=2,
        feat_channels=256,
        cls_loss=dict(type='CrossEntropyLoss', loss_weight=1.0),
        reg_loss=dict(type='L1Loss', loss_weight=1.0),
    )
)
test_cfg = dict(
    z_size=127,
    x_size=255,
    z_feat_size=6,
    x_feat_size=22,
    search_region=dict(num_scales=1, scale_step=1.0, context_amount=0.5),
    min_box_size=8,
    penalty_k=0.2,
    min_score_threshold=0.1,
    linear_inter_rate=0.5,
    window=dict(norm_size=144, weight=0.40),
    proposal=dict(
        score_thr=0.0,
        nms_iou_thr=0.6,
        max_num_per_img=8,
    ),
    fm_score_weight=0.5,
)
train_cfg = dict(
    type='PairwiseWrapper',
    samples_per_gpu=8,
    workers_per_gpu=4,
    z_size=255,
    x_size=255,
    z_feat_size=6,
    x_feat_size=22,
    num_freeze_blocks=0,
    rpn=dict(
        assigner=dict(type='MaxIoUAssigner', pos_iou_thr=0.60, neg_iou_thr=0.30, min_pos_iou=0.5, ignore_iof_thr=-1),
        sampler=dict(type='RandomSampler', num=64, pos_fraction=0.25, neg_pos_ub=-1, ),
        pos_weight=-1,
    ),
    proposal=dict(
        score_thr=0.0,
        nms_iou_thr=0.75,
        max_num_per_img=12,
    ),
    compare=dict(
        assigner=dict(type='MaxIoUAssigner', pos_iou_thr=0.50, neg_iou_thr=0.45, min_pos_iou=0.45, ignore_iof_thr=-1),
        sampler=dict(type='PseudoSampler'),
        pos_weight=-1,
    ),
    # optimizer
    optimizer=dict(type='SGD', lr=0.01, weight_decay=0.0001),
    optimizer_config=dict(
        grad_clip=dict(max_norm=20, norm_type=2),
        optimizer_cfg=dict(
            type='SGD',
            params=[dict(name='head/weight'), dict(name='head/bias', weight_decay=0.0)],
            lr=0.01,
            weight_decay=0.0001
        ),
        optimizer_schedule=[
            dict(
                start_epoch=1,
                type='SGD',
                params=[dict(name='all/weight'), dict(name='all/bias', weight_decay=0.0)],
                lr=0.01,
                weight_decay=0.0001
            )
        ]
    ),
    # learning policy
    lr_config=dict(
        policy='step',
        gamma=0.1,
        step=[25, 45],
        warmup='linear',
        warmup_iters=100,
        warmup_ratio=0.1 / 3,
    ),
    checkpoint_config=dict(interval=1),
    log_config=dict(
        interval=100,
        hooks=[
            dict(type='TextLoggerHook'),
        ]
    ),
    total_epochs=50,
    workflow=[('train', 1)],
)

storage_backend = dict(type='ZipWrapper', cache_into_memory=True)
train_cfg['train_data'] = get_data_config(train_cfg['z_size'], train_cfg['x_size'], data_root, storage_backend)
