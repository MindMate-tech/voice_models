# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 16:52:17 2020

@author: Iluva
"""
import torch
import torch.nn as nn

class TCN(nn.Module):
    """
    TCN class;
    """
    def __init__(self, device):
        """
        init method;
        """
        super(TCN, self).__init__()
        self.device = device     # 'cpu' or 'cuda:x'
        self.tcn = nn.Sequential(
            # nn.BatchNorm1d(13),
            nn.Conv1d(in_channels=13, out_channels=32, kernel_size=1, stride=1, padding=0),
            # nn.BatchNorm1d(32),
            nn.Conv1d(in_channels=32, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.Conv1d(in_channels=32, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=4, stride=4, padding=0),
            # nn.Dropout(),
            # nn.BatchNorm1d(32),
            nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.Conv1d(in_channels=64, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=4, stride=4, padding=0),
            # nn.Dropout(),
            # nn.BatchNorm1d(64),
            nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.Conv1d(in_channels=128, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=4, stride=4, padding=0),
            # nn.BatchNorm1d(128),
            nn.Conv1d(in_channels=128, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.Conv1d(in_channels=128, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=4, stride=4, padding=0),
            # nn.BatchNorm1d(128),
            nn.Conv1d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.Conv1d(in_channels=256, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=4, stride=4, padding=0),
            # nn.BatchNorm1d(256),
            nn.Conv1d(in_channels=256, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.Conv1d(in_channels=256, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=4, stride=4, padding=0),
            # nn.BatchNorm1d(256),
            nn.Conv1d(in_channels=256, out_channels=512, kernel_size=3, stride=1, padding=1),
            nn.Conv1d(in_channels=512, out_channels=512, kernel_size=3, stride=1, padding=1),
            nn.ELU(),
            nn.MaxPool1d(kernel_size=4, stride=4, padding=0),
            # nn.BatchNorm1d(512),
            nn.Conv1d(in_channels=512, out_channels=512, kernel_size=3, stride=1, padding=1),
            nn.Conv1d(in_channels=512, out_channels=512, kernel_size=3, stride=1, padding=1),
            nn.ELU(),
        )
        # linear layer
        self.mlp = nn.Sequential(
            nn.Linear(512, 2, bias=False)
        )
        self.tcn.to(device)
        self.mlp.to(device)

    def forward(self, Xs):
        """
        pass fwd;
        """
        out = []
        for idx, X in enumerate(Xs):
            # Validate input shape before processing
            # All sequences should be normalized to exactly 16384 in reformat()
            if X.shape[2] != 16384:
                raise ValueError(
                    f"Input sequence length {X.shape[2]} is not equal to safe length 16384. "
                    f"Shape: {X.shape}, Index: {idx}. "
                    f"Please ensure sequences are normalized to 16384 in reformat()."
                )
            try:
                tmp = self.tcn(X)
                # global average pooling
                tmp = torch.mean(tmp, dim=2)
                # linear layer
                tmp = self.mlp(tmp)
                tmp = tmp.squeeze()
                out.append(tmp)
            except RuntimeError as e:
                if "max_pool1d" in str(e) and "Invalid computed output size" in str(e):
                    raise RuntimeError(
                        f"MaxPool1d error for input at index {idx} with shape {X.shape}. "
                        f"Sequence length {X.shape[2]} may be too short. "
                        f"Original error: {e}"
                    ) from e
                raise
        out = torch.stack(out)
        return out

    def forward_wo_gpool(self, Xs):
        """
        fwd without gpool;
        """
        out = []
        for X in Xs:
            tmp = self.tcn(X)
            out.append(tmp)
        return out

    def get_scores(self, Xs):
        """
        get scores;
        """
        return self(Xs)

    def get_scores_loss(self, Xs, ys, loss_fn):
        """
        get scores and loss;
        """
        scores = self.get_scores(Xs)
        loss = loss_fn(scores, ys)
        return scores, loss

    def reformat(self, Xs, _):
        """
        reformat Xs array accordingly;
        """
        # CRITICAL: Pad ALL sequences to a safe length to avoid MaxPool1d errors
        # The TCN has 7 MaxPool1d layers (kernel_size=4, stride=4)
        # Each MaxPool1d divides length by 4, so we need at least 4^7 = 16384 frames
        # To be absolutely safe, we pad ALL sequences to 16384 frames
        # This ensures no sequence will fail, regardless of its original length
        SAFE_SEQ_LENGTH = 16384  # Safe length for 7 MaxPool1d layers (4^7)
        
        for idx, _ in enumerate(Xs):
            # Convert to tensor (handle numpy arrays)
            if not isinstance(Xs[idx], torch.Tensor):
                Xs[idx] = torch.tensor(Xs[idx], dtype=torch.float32, device=self.device)
            else:
                Xs[idx] = Xs[idx].to(dtype=torch.float32, device=self.device)
            
            # Ensure 2D shape: (seq_len, 13) or (13, seq_len)
            if Xs[idx].dim() != 2:
                raise ValueError(f"Expected 2D tensor, got {Xs[idx].dim()}D with shape {Xs[idx].shape}")
            
            # Permute if needed: (seq_len, 13) -> (13, seq_len)
            if Xs[idx].shape[0] != 13:
                if Xs[idx].shape[1] == 13:
                    # In (seq_len, 13) format, need to permute
                    Xs[idx] = Xs[idx].permute(1, 0)
                else:
                    raise ValueError(
                        f"Unexpected tensor shape {Xs[idx].shape}. "
                        f"Expected (seq_len, 13) or (13, seq_len)"
                    )
            
            # Get current sequence length
            seq_length = Xs[idx].shape[1]
            
            # CRITICAL: ALWAYS pad to SAFE_SEQ_LENGTH, regardless of current length
            # This is the safest approach to avoid any MaxPool1d errors
            # We pad ALL sequences to exactly 5000 to ensure consistency
            if seq_length < SAFE_SEQ_LENGTH:
                # Pad with zeros at the end to reach SAFE_SEQ_LENGTH
                padding_size = SAFE_SEQ_LENGTH - seq_length
                padding = torch.zeros(Xs[idx].shape[0], padding_size, 
                                     dtype=Xs[idx].dtype, device=self.device)
                Xs[idx] = torch.cat([Xs[idx], padding], dim=1)
            elif seq_length > SAFE_SEQ_LENGTH:
                # For sequences longer than 5000, truncate to 5000 to ensure consistency
                # This prevents any edge cases with very long sequences
                Xs[idx] = Xs[idx][:, :SAFE_SEQ_LENGTH]
            
            # At this point, seq_length should be exactly SAFE_SEQ_LENGTH
            assert Xs[idx].shape[1] == SAFE_SEQ_LENGTH, \
                f"Expected sequence length {SAFE_SEQ_LENGTH}, got {Xs[idx].shape[1]}"
            
            # Reshape to (1, 13, seq_len) for batch processing
            Xs[idx] = Xs[idx].view(1, Xs[idx].shape[0], Xs[idx].shape[1])
            
            # Final validation - ensure we have exactly the safe length
            final_length = Xs[idx].shape[2]
            if final_length != SAFE_SEQ_LENGTH:
                raise ValueError(
                    f"Final sequence length {final_length} is not equal to safe length {SAFE_SEQ_LENGTH}. "
                    f"This should not happen. Shape: {Xs[idx].shape}"
                )
