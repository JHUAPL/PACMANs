"""
Copyright 2022, The Johns Hopkins University Applied Physics Laboratory LLC
All rights reserved.
Distributed under the terms of the BSD 3-Clause License.

Approved for public release; distribution is unlimited.
This material is based upon work supported by the Defense Advanced Research Projects Agency (DARPA) under Agreement No.
HR00112290032.

Implementation based on:
Ghosh, Arnab, Viveka Kulharia, Vinay P. Namboodiri, Philip HS Torr, and Puneet K. Dokania. "Multi-agent diverse generative adversarial networks." In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 8513-8521. 2018.
"""

import sys
import pickle

import numpy as np
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import classification_report

import torch
from torch.optim import Adam
from torch.utils.data import Dataset, DataLoader

from generators.generator_adv import GeneratorBase, GeneratorAdv
from discriminators.discriminator_mad_clf import DiscriminatorBase, DiscriminatorMADClf
from gan_utils.label_funcs import get_gen_mad_labels, get_disc_mad_labels, get_gen_soft_clf_labels, get_disc_clf_labels

class GANTrainer(object):

	class ShutoffDataset(Dataset):
		def __init__(self, seeds, labels):
			self.seeds = seeds
			self.labels = labels

		def __len__(self):
			return len(self.labels)

		def __getitem__(self, idx):
			return self.seeds[idx], self.labels[idx]


	def __init__(self, n_gens, x_size, class_names, z_size, surrogate_model, gen_loss_func, disc_loss_func,
				gen_mad_label_func=get_gen_mad_labels, disc_mad_label_func=get_disc_mad_labels, 
				gen_clf_label_func=get_gen_soft_clf_labels, disc_clf_label_func=get_disc_clf_labels,
				h_sizes_gen_base=[128, 128], h_sizes_gen_head=[], h_sizes_disc_base=[128, 128], h_sizes_disc_head=[], mb_disc_out=128,
				lr=1e-4, samples_per_mode=128, load_data_path='', chkpt_idx=0, device=0, use_class_wts=True, test_split=0.2,
    			save_dir='./tmp', save_subdir = 'nonparam_density', chkpt_subdir='chkpts', chkpt_freq=25000):

		# Initialize placeholders
		self.n_gens = n_gens
		self.x_size = x_size
		self.z_size = z_size
		self.class_names = class_names
		self.n_classes = len(class_names)
		self.samples_per_mode = samples_per_mode

		self.save_dir = save_dir
		self.save_subdir = save_subdir
		self.chkpt_subdir = chkpt_subdir
		self.chkpt_freq = chkpt_freq

		# Labelling and loss functions
		self.gen_label_funcs = {"mad_gan": gen_mad_label_func,
								"clf": gen_clf_label_func
								}
		self.disc_label_funcs = {"mad_gan": disc_mad_label_func,
								 "clf": disc_clf_label_func
								}
		self.gen_loss_func = gen_loss_func
		self.disc_loss_func = disc_loss_func
		self.gen_losses = {k:[] for k in range(self.n_gens)}
		self.disc_losses = []
		self.disc_metrics = {"train": [], "test": []}

		self.surrogate_model = surrogate_model

		# Get device
		if device is None:
			self.device = torch.device("cpu")
		else:
			self.device = torch.device(f'cuda:{device}' if torch.cuda.is_available() else 'cpu')
		print(self.device)
		# Initialize generators
		self.gen_base = GeneratorBase(z_size=z_size, h_sizes=h_sizes_gen_base)
		self.gen_base.double()
		self.gens = [GeneratorAdv(self.gen_base, h_sizes=h_sizes_gen_head, out_size=x_size).to(self.device) for _ in range(self.n_gens)]
		[g.double() for g in self.gens]

		# Initialize discriminator
		self.disc_base = DiscriminatorBase(in_size=self.x_size, h_sizes=h_sizes_disc_base)
		self.disc = DiscriminatorMADClf(disc_base=self.disc_base, n_classes=self.n_classes, mb_disc_out=mb_disc_out, n_modes=self.n_gens, h_sizes=h_sizes_disc_head).to(self.device)
		self.disc.double()

		# Initialize optimizers
		self.optim_g = [Adam(self.gens[i].parameters(), lr=lr) for i in range(self.n_gens)]
		self.optim_d = Adam(self.disc.parameters(), lr=lr)

		# Load model checkpoint
		self.chkpt_idx = chkpt_idx
		if chkpt_idx > 0:
			print(f'Loading checkpoint {chkpt_idx}...')
			self.load_models(chkpt_idx)

		# Load real data
		self.train_dataset, self.test_dataset, self.train_labels, self.test_labels = None, None, None, None
		if load_data_path:
			with open(load_data_path, 'rb') as f:
				data_dict = pickle.load(f)
			# self.gmm = data_dict['gmm']
			self.real_dataset = data_dict['sample']
			self.real_labels = data_dict['labels']
			if 'scaler' in data_dict:
				self.ic_param_scaler = data_dict['scaler']
			else:
				self.ic_param_scaler = None

			# Load training and test splits
			if 'train_sample' and 'train_labels' in data_dict:
				print("Loading training data...")
				self.train_dataset, self.train_labels = data_dict['train_sample'], data_dict['train_labels']
			if 'train_sample' and 'train_labels' in data_dict:
				print("Loading test data...")
				self.test_dataset, self.test_labels = data_dict['test_sample'], data_dict['test_labels']
		if use_class_wts:
			self.class_wts = torch.DoubleTensor(compute_class_weight('balanced', classes=np.unique(self.real_labels), y=self.real_labels)).to(self.device)
		else:
			self.class_wts = None

	def load_models(self, chkpt_idx=None):
		if chkpt_idx == None:
			chkpt_idx = self.chkpt_idx

		# Generate load path
		model_save_path = f'{self.save_dir}/{self.save_subdir}/{self.chkpt_subdir}'

		# Save generator state dict
		print(f'Loading generator checkpoint for epoch {chkpt_idx}...')
		for i in range(self.n_gens):
			self.gens[i].load_state_dict(torch.load(f'{model_save_path}/gen_{i}_{chkpt_idx}.pt', map_location=self.device))
			self.optim_g[i].load_state_dict(torch.load(f'{model_save_path}/gen_opt_{i}_{chkpt_idx}.pt', map_location=self.device))
		with open(f'{model_save_path}/gens_losses_{chkpt_idx}.pkl', 'rb') as f:
			self.gen_losses = pickle.load(f)

		# Save discriminator state dict
		print(f'Loading discriminator checkpoint for epoch {chkpt_idx}...')
		self.disc.load_state_dict(torch.load(f'{model_save_path}/disc_{chkpt_idx}.pt', map_location=self.device))
		self.optim_d.load_state_dict(torch.load(f'{model_save_path}/disc_opt_{chkpt_idx}.pt', map_location=self.device))

		with open(f'{model_save_path}/disc_losses_{chkpt_idx}.pkl', 'rb') as f:
			self.disc_losses = pickle.load(f)
		with open(f'{model_save_path}/disc_metrics_{chkpt_idx}.pkl', 'rb') as f:
			self.disc_metrics = pickle.load(f)

	def save_models(self, chkpt_idx):
		# Generate save path
		model_save_path = f'{self.save_dir}/{self.save_subdir}/{self.chkpt_subdir}'

		# Save generator state dict
		print(f'Saving generator checkpoint for epoch {chkpt_idx}...')
		for i in range(self.n_gens):
			torch.save(self.gens[i].state_dict(), f'{model_save_path}/gen_{i}_{chkpt_idx}.pt')
			torch.save(self.optim_g[i].state_dict(), f'{model_save_path}/gen_opt_{i}_{chkpt_idx}.pt')
		with open(f'{model_save_path}/gens_losses_{chkpt_idx}.pkl', 'wb') as f:
			pickle.dump(self.gen_losses, f, protocol=pickle.HIGHEST_PROTOCOL)

		# Save discriminator state dict
		print(f'Saving discriminator checkpoint for epoch {chkpt_idx}...')
		torch.save(self.disc.state_dict(), f'{model_save_path}/disc_{chkpt_idx}.pt')
		torch.save(self.optim_d.state_dict(), f'{model_save_path}/disc_opt_{chkpt_idx}.pt')

		with open(f'{model_save_path}/disc_losses_{chkpt_idx}.pkl', 'wb') as f:
			pickle.dump(self.disc_losses, f, protocol=pickle.HIGHEST_PROTOCOL)
		with open(f'{model_save_path}/disc_metrics_{chkpt_idx}.pkl', 'wb') as f:
			pickle.dump(self.disc_metrics, f, protocol=pickle.HIGHEST_PROTOCOL)

	def compute_state_changes(self, ic_params, return_tensors=True, debug=False):
		# Pass ic_params through surrogate
		solutions = self.surrogate_model(ic_params, debug=debug)

		# Evaluate whether a shutoff occurred or not using self.label_func -> should take the solutions as arguments
		is_shutoff = self.disc_label_funcs["clf"](solutions)

		# Return ground-truth as tensors
		if return_tensors:
			is_shutoff = torch.LongTensor(is_shutoff)

		return is_shutoff

	def compute_disc_metrics(self, train_data, train_labels, test_data=None, test_labels=None, batch_size=128):
		# Set discriminator to eval mode
		self.disc.eval()

		# Normalize data
		if self.ic_param_scaler != None:
			train_data = self.ic_param_scaler.transform(train_data)
			test_data = self.ic_param_scaler.transform(test_data)

		# Compute metrics for training data
		train_clf_logits = []
		test_clf_logits = []
		with torch.inference_mode():


			i = 0
			while i < test_data.shape[0]:
				# Compute logits
				test_batch_pt = torch.DoubleTensor(test_data[i:i+batch_size]).to(self.device)
				_, test_batch_clf_logits = self.disc(test_batch_pt)
				test_clf_logits.append(test_batch_clf_logits)
				i += batch_size

			# Get predictions
			test_clf_logits = torch.cat(test_clf_logits, dim=0)
			test_clf_preds = torch.argmax(test_clf_logits, axis=1).detach().cpu().numpy()

			# Compute precision, recall, f1-score
			test_clf_report = classification_report(test_labels, test_clf_preds, target_names=self.class_names,
													output_dict=True, zero_division=0)
			# self.disc_metrics["train"].append(train_clf_report)
			self.disc_metrics["test"].append(test_clf_report)

	def train(self, gen_mb_size=None, real_mb_size=128, n_iterations=198000, chkpt_freq = None, debug=False):
		if gen_mb_size is None:
			gen_mb_size = self.samples_per_mode
		if chkpt_freq is None:
			chkpt_freq = self.chkpt_freq

		# Get training data
		if self.train_dataset is None:
			train_dataset = self.real_dataset
			train_labels = self.real_labels
		else:
			train_dataset = self.train_dataset
			train_labels = self.train_labels

		# Normalize training data
		if self.ic_param_scaler != None:
			print("Normalizing data...")
			train_dataset = self.ic_param_scaler.transform(train_dataset)

		# Create dataset
		train_dataset = self.ShutoffDataset(train_dataset, train_labels)

		# Create dataloader for real dataset
		train_dataloader = DataLoader(train_dataset, batch_size=real_mb_size, shuffle=True)

		for i in range(n_iterations):
			# Set models in training mode
			[g.train() for g in self.gens]
			self.disc.train()
			# Checkpoint
			if (i % chkpt_freq) == 0:
				self.save_models(i+self.chkpt_idx)

			gen_mb_losses = {k:[] for k in range(self.n_gens)}
			disc_mb_losses = []
			count = 0
			for real_seed, real_label in train_dataloader:
				if debug:
					if count == 5:
						break
				real_seed, real_label = real_seed.to(self.device), real_label.long().to(self.device)

				# Get batch size
				mb_size = min(gen_mb_size, real_seed.shape[0])

				# Create discriminator MAD-GAN labels
				disc_mad_labels = self.disc_label_funcs["mad_gan"](mb_size, self.n_gens, self.device)

				# Train each generator
				x_fake_agg = []
				for gen_idx in range(self.n_gens):
					# print(gen_idx)
					# Create random noise
					z = torch.rand(mb_size, self.z_size).uniform_(-1.0, 1.0).double().to(self.device)

					# Create training labels for generator (MAD-GAN and shutoff labels)
					gen_mad_labels = self.gen_label_funcs["mad_gan"](mb_size, self.n_gens, self.device)
					gen_clf_labels = self.gen_label_funcs["clf"](mb_size, self.n_classes, self.device)

					# Zero-out generator gradients
					self.optim_g[gen_idx].zero_grad()

					# Generate fake seeds
					x_fake = self.gens[gen_idx](z)

					# Compute logits for generator
					gen_mad_logits, gen_clf_logits = self.disc(x_fake)

					# Evaluate cross entropy losses
					# mad_loss = torch.nn.functional.cross_entropy(gen_mad_logits, gen_mad_labels)
					# clf_loss = torch.nn.functional.cross_entropy(gen_clf_logits, gen_clf_labels, weight=self.class_wts)

					# Add both losses
					gen_loss = self.gen_loss_func(gen_mad_logits, gen_mad_labels, gen_clf_logits, gen_clf_labels, self.class_wts)

					if gen_idx < (self.n_gens - 1):
						gen_loss.backward(retain_graph=True)
					else:
						gen_loss.backward()

					self.optim_g[gen_idx].step()
					x_fake_agg.append(x_fake)
					gen_mb_losses[gen_idx].append(gen_loss.item())

				# Compute ground-truth shutoff labels, using surrogate model
				# Concatenate x_fake_agg
				x_fake_agg = torch.cat(x_fake_agg, axis=0).detach()

				# Transform seeds
				x_fake_icp = x_fake_agg.clone().cpu().numpy()
				if self.ic_param_scaler is not None:
					x_fake_icp = self.ic_param_scaler.inverse_transform(x_fake_icp)

				# Create labels
				x_fake_labels = self.compute_state_changes(x_fake_icp, debug=debug).to(self.device)
				if self.surrogate_model.constants_dict["noise_amplification"] > 0.0:
					x_real_icp = real_seed.clone().cpu().numpy()
					if self.ic_param_scaler is not None:
						x_real_icp = self.ic_param_scaler.inverse_transform(x_real_icp)
					real_label = self.compute_state_changes(x_real_icp, debug=debug).to(self.device)

				# Zero-out gradients for discriminator
				self.optim_d.zero_grad()

				# Add real data to device
				x_real_agg = real_seed

				# Create disc_clf_labels by concatenating generated/real ground truths
				disc_clf_labels = torch.cat((x_fake_labels, real_label), axis=0)

				# Compute discriminator logits for real and fake samples
				fake_mad_logits, fake_clf_logits = self.disc(x_fake_agg.detach())
				real_mad_logits, real_clf_logits = self.disc(x_real_agg)
				disc_mad_logits = torch.cat((fake_mad_logits, real_mad_logits), axis=0)
				disc_clf_logits = torch.cat((fake_clf_logits, real_clf_logits), axis=0)

				# Compute discriminator loss, gradients, update discriminator
				disc_loss = self.disc_loss_func(disc_mad_logits, disc_mad_labels, disc_clf_logits, disc_clf_labels, self.class_wts)

				disc_mb_losses.append(disc_loss.item())
				disc_loss.backward()
				self.optim_d.step()

				if debug:
					count += 1

			# Update loss history
			disc_epoch_loss = sum(disc_mb_losses)/len(disc_mb_losses)
			self.disc_losses.append(disc_epoch_loss)
			gen_epoch_loss = []
			for gen_idx in range(self.n_gens):
				gen_idx_epoch_loss = sum(gen_mb_losses[gen_idx])/len(gen_mb_losses[gen_idx])
				gen_epoch_loss.append(gen_idx_epoch_loss)
				self.gen_losses[gen_idx].append(gen_idx_epoch_loss)

			# Compute discriminator metrics
			print("Computing discriminator metrics on real dataset...")
			if self.test_dataset is not None and self.test_labels is not None:
				self.compute_disc_metrics(self.train_dataset, self.train_labels, self.test_dataset, self.test_labels)
			else:
				self.compute_disc_metrics(self.real_dataset, self.real_labels)
			print('Epoch: ', i+1)
			print('Generator loss: ', sum(gen_epoch_loss)/len(gen_epoch_loss))
			print('Discriminator loss: ', disc_epoch_loss, '\n')
			# print('Discriminator clf train metrics: ', self.disc_metrics["train"][i], "\n")
			print('Discriminator clf test metrics: ', self.disc_metrics["test"][i], "\n")

		# Save at the end of training
		self.save_models(i+self.chkpt_idx+1)

		# Update checkpoint idx
		self.chkpt_idx += n_iterations
