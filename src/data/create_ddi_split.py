import os
import numpy as np

print("=" * 60)
print("CREATING DDI TRAIN / VALIDATION / TEST SPLIT")
print("=" * 60)

INPUT_PATH = "datasets/final/multiview_dataset.npz"
OUTPUT_PATH = "datasets/final/ddi_split.npz"

SEED = 42
rng = np.random.default_rng(SEED)

# ============================================================
# LOAD DATA
# ============================================================

data = np.load(INPUT_PATH)

drug_ids = data["drug_ids"]
chemical_features = data["chemical_features"]
pathway_features = data["pathway_features"]
smiles_sequences = data["smiles_sequences"]
smiles_available = data["smiles_available"]
smiles_missing = data["smiles_missing"]
edge_index = data["edge_index"]

num_nodes = len(drug_ids)

print(f"Number of drugs : {num_nodes}")
print(f"Original edges  : {edge_index.shape[1]}")

# ============================================================
# CREATE UNIQUE UNDIRECTED POSITIVE EDGES
# ============================================================

src = edge_index[0]
dst = edge_index[1]

# Remove self-loops
mask = src != dst
src = src[mask]
dst = dst[mask]

# Canonical order
small = np.minimum(src, dst)
large = np.maximum(src, dst)

positive_pairs = np.unique(
    np.stack([small, large], axis=1),
    axis=0
)

positive_edges = positive_pairs.T

num_positive = positive_edges.shape[1]

print(f"Unique positive edges : {num_positive}")

# ============================================================
# SHUFFLE POSITIVE EDGES
# ============================================================

indices = np.arange(num_positive)
rng.shuffle(indices)

positive_edges = positive_edges[:, indices]

# ============================================================
# 80 / 10 / 10 SPLIT
# ============================================================

train_end = int(num_positive * 0.80)
val_end = int(num_positive * 0.90)

train_pos = positive_edges[:, :train_end]
val_pos = positive_edges[:, train_end:val_end]
test_pos = positive_edges[:, val_end:]

print()
print("POSITIVE EDGE SPLIT")
print(f"Train : {train_pos.shape[1]}")
print(f"Val   : {val_pos.shape[1]}")
print(f"Test  : {test_pos.shape[1]}")

# ============================================================
# CREATE POSITIVE EDGE SET
# ============================================================

positive_set = set(
    zip(
        positive_edges[0],
        positive_edges[1]
    )
)

# ============================================================
# GENERATE EXACT NUMBER OF UNIQUE NEGATIVE EDGES
# ============================================================

required_negative = num_positive

negative_set = set()

print()
print("Generating negative edges...")

while len(negative_set) < required_negative:

    remaining = required_negative - len(negative_set)

    batch_size = max(remaining * 2, 10000)

    random_src = rng.integers(
        0,
        num_nodes,
        size=batch_size
    )

    random_dst = rng.integers(
        0,
        num_nodes,
        size=batch_size
    )

    for a, b in zip(random_src, random_dst):

        # No self-loop
        if a == b:
            continue

        # Make undirected canonical pair
        if a > b:
            a, b = b, a

        pair = (int(a), int(b))

        # Must not be a positive DDI
        if pair in positive_set:
            continue

        # Must be unique
        negative_set.add(pair)

        if len(negative_set) >= required_negative:
            break

    print(
        f"\rNegative edges generated: "
        f"{len(negative_set)}/{required_negative}",
        end=""
    )

print()

# ============================================================
# CONVERT NEGATIVES TO ARRAY
# ============================================================

negative_edges = np.array(
    list(negative_set),
    dtype=np.int64
).T

# Shuffle
indices = np.arange(required_negative)
rng.shuffle(indices)

negative_edges = negative_edges[:, indices]

# ============================================================
# SPLIT NEGATIVES
# ============================================================

train_neg = negative_edges[:, :train_end]

val_neg = negative_edges[:, train_end:val_end]

test_neg = negative_edges[:, val_end:]

print()
print("NEGATIVE EDGE SPLIT")
print(f"Train : {train_neg.shape[1]}")
print(f"Val   : {val_neg.shape[1]}")
print(f"Test  : {test_neg.shape[1]}")

# ============================================================
# CREATE LABELLED DATASETS
# ============================================================

train_edges = np.concatenate(
    [train_pos, train_neg],
    axis=1
)

val_edges = np.concatenate(
    [val_pos, val_neg],
    axis=1
)

test_edges = np.concatenate(
    [test_pos, test_neg],
    axis=1
)

train_labels = np.concatenate([
    np.ones(train_pos.shape[1], dtype=np.float32),
    np.zeros(train_neg.shape[1], dtype=np.float32)
])

val_labels = np.concatenate([
    np.ones(val_pos.shape[1], dtype=np.float32),
    np.zeros(val_neg.shape[1], dtype=np.float32)
])

test_labels = np.concatenate([
    np.ones(test_pos.shape[1], dtype=np.float32),
    np.zeros(test_neg.shape[1], dtype=np.float32)
])

# ============================================================
# SHUFFLE EACH DATASET
# ============================================================

def shuffle_split(edges, labels):

    idx = np.arange(edges.shape[1])
    rng.shuffle(idx)

    return edges[:, idx], labels[idx]


train_edges, train_labels = shuffle_split(
    train_edges,
    train_labels
)

val_edges, val_labels = shuffle_split(
    val_edges,
    val_labels
)

test_edges, test_labels = shuffle_split(
    test_edges,
    test_labels
)

# ============================================================
# TRAINING GRAPH
# ============================================================
# ONLY training positive edges are visible to GNN.
# Validation/test positive edges are hidden.

train_graph_edges = train_pos

# ============================================================
# VALIDATION
# ============================================================

print()
print("=" * 60)
print("FINAL SPLIT SUMMARY")
print("=" * 60)

print(f"Nodes                : {num_nodes}")
print(f"Training graph edges : {train_graph_edges.shape[1]}")

print()
print("Train")
print(f"  Total edges : {train_edges.shape[1]}")
print(f"  Positive    : {int(train_labels.sum())}")
print(f"  Negative    : {int((train_labels == 0).sum())}")

print()
print("Validation")
print(f"  Total edges : {val_edges.shape[1]}")
print(f"  Positive    : {int(val_labels.sum())}")
print(f"  Negative    : {int((val_labels == 0).sum())}")

print()
print("Test")
print(f"  Total edges : {test_edges.shape[1]}")
print(f"  Positive    : {int(test_labels.sum())}")
print(f"  Negative    : {int((test_labels == 0).sum())}")

# ============================================================
# SAVE
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
    exist_ok=True
)

np.savez_compressed(
    OUTPUT_PATH,

    drug_ids=drug_ids,

    chemical_features=chemical_features,

    pathway_features=pathway_features,

    smiles_sequences=smiles_sequences,

    smiles_available=smiles_available,

    smiles_missing=smiles_missing,

    train_graph_edges=train_graph_edges,

    train_edges=train_edges,
    train_labels=train_labels,

    val_edges=val_edges,
    val_labels=val_labels,

    test_edges=test_edges,
    test_labels=test_labels
)

print()
print("=" * 60)
print("DDI SPLIT CREATED SUCCESSFULLY")
print("=" * 60)

print()
print("Saved:")
print(OUTPUT_PATH)