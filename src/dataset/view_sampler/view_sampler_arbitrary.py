from dataclasses import dataclass
from typing import Literal

import torch
from jaxtyping import Float, Int64
from torch import Tensor

from .additional_view_hack import add_addtional_context_index
from .view_sampler import ViewSampler


@dataclass
class ViewSamplerArbitraryCfg:
    name: Literal["arbitrary"]
    num_context_views: int
    num_target_views: int
    context_views: list[int] | None
    target_views: list[int] | None


class ViewSamplerArbitrary(ViewSampler[ViewSamplerArbitraryCfg]):
    def sample(
        self,
        scene: str,
        extrinsics: Float[Tensor, "view 4 4"],
        intrinsics: Float[Tensor, "view 3 3"],
        device: torch.device = torch.device("cpu"),
    ) -> tuple[
        Int64[Tensor, " context_view"],  # indices for context views
        Int64[Tensor, " target_view"],  # indices for target views
        Float[Tensor, " overlap"],  # overlap
    ]:
        """Arbitrarily sample context and target views."""
        num_views, _, _ = extrinsics.shape

        index_context = torch.randint(
            0,
            num_views,
            size=(self.cfg.num_context_views,),
            device=device,
        )

        # Allow the context views to be fixed.
        if self.cfg.context_views is not None:
            index_context = torch.tensor(
                self.cfg.context_views, dtype=torch.int64, device=device
            )

            if self.cfg.num_context_views >= 3 and len(self.cfg.context_views) == 2:
                index_context = add_addtional_context_index(index_context, self.cfg.num_context_views)
            else:
                assert len(self.cfg.context_views) == self.cfg.num_context_views
        index_target = torch.randint(
            0,
            num_views,
            size=(self.cfg.num_target_views,),
            device=device,
        )

        # Allow the target views to be fixed.
        if self.cfg.target_views is not None:
            assert len(self.cfg.target_views) == self.cfg.num_target_views
            index_target = torch.tensor(
                self.cfg.target_views, dtype=torch.int64, device=device
            )

        overlap = torch.tensor([0.5], dtype=torch.float32, device=device)  # dummy

        return index_context, index_target, overlap

    @property
    def num_context_views(self) -> int:
        return self.cfg.num_context_views

    @property
    def num_target_views(self) -> int:
        return self.cfg.num_target_views
