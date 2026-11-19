import json
from pathlib import Path

from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download
from safetensors.torch import load_file, save
from torch import Tensor

REPO_NAME = "sehyunpark73/cartridge-teacher-size"


def upload_file(
    path: str,
    data: bytes,
) -> None:
    HfApi().upload_file(path_or_fileobj=data, path_in_repo=path, repo_id=REPO_NAME, commit_message=f"save {path}")
    print(f"saved {path}")


def download_file(
    path: str,
) -> str:
    return hf_hub_download(REPO_NAME, path)


def list_files() -> set[str]:
    return set(HfApi().list_repo_files(REPO_NAME))


def save_synthesis(
    hub_path: str,
    rows: list[dict],
    tensors: dict[str, Tensor],
) -> None:
    # rows와 tensors는 한 commit으로 저장
    operations = [
        CommitOperationAdd(path_in_repo=f"{hub_path}/rows.json", path_or_fileobj=json.dumps(rows, indent=2).encode()),
        CommitOperationAdd(path_in_repo=f"{hub_path}/logprobs.safetensors", path_or_fileobj=save(tensors)),
    ]
    HfApi().create_commit(REPO_NAME, operations=operations, commit_message=f"save {hub_path}")
    print(f"saved {hub_path}")


def save_result(
    hub_path: str,
    file_name: str,
    result: dict,
) -> None:
    upload_file(f"{hub_path}/{file_name}.json", json.dumps(result, indent=2).encode())


def load_result(
    hub_path: str,
    file_name: str,
) -> dict:
    return json.loads(Path(download_file(f"{hub_path}/{file_name}.json")).read_text())


def save_tensors(
    hub_path: str,
    file_name: str,
    tensors: dict[str, Tensor],
) -> None:
    upload_file(f"{hub_path}/{file_name}.safetensors", save({name: tensor.detach().cpu().contiguous() for name, tensor in tensors.items()}))


def load_tensors(
    hub_path: str,
    file_name: str,
) -> dict[str, Tensor]:
    return load_file(download_file(f"{hub_path}/{file_name}.safetensors"))


def get_pending_targets(
    experiment_name: str,
    model_name: str,
    file_name: str,
) -> list[str]:
    # base, icl과 hub에 있는 cartridge 중 experiment_name의 file_name 결과가 없는 것
    # 예시) ["base/Llama-3.2-3B-Instruct", "cartridge/Llama-3.2-3B-Instruct/teacher=..."]
    files = list_files()
    targets = [f"base/{model_name}", f"icl/{model_name}"]
    targets += sorted(str(Path(file).parent) for file in files if file.startswith(f"cartridge/{model_name}/") and file.endswith("/cartridge.safetensors"))
    return [target for target in targets if f"{experiment_name}/{target}/{file_name}.json" not in files]
