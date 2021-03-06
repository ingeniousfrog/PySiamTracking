# Copyright 2018-2019 Open-MMLab. All rights reserved.
# Licensed under the Apache License, Version 2.0.


import os
from .hook import Hook


class CheckpointHook(Hook):

    def __init__(self,
                 interval=-1,
                 save_optimizer=True,
                 out_dir=None,
                 **kwargs):
        self.interval = interval
        self.save_optimizer = save_optimizer
        self.out_dir = out_dir
        self.args = kwargs

    def before_run(self, runner):
        if not self.out_dir:
            self.out_dir = runner.work_dir
        if os.path.isdir(self.out_dir):
            checkpoint_path = os.path.join(self.out_dir, 'latest.pth')
            if os.path.exists(checkpoint_path):
                runner.resume(checkpoint_path)

    def after_train_epoch(self, runner):
        if not self.every_n_epochs(runner, self.interval):
            return

        if not self.out_dir:
            self.out_dir = runner.work_dir
        runner.save_checkpoint(
            self.out_dir, save_optimizer=self.save_optimizer, **self.args)
