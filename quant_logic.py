import numpy as np

def detect_liquidity_vacuum(bids, asks):
    """
    Physics: Kinematics of the Order Book.
    Detects 'holes' in the 50 levels where price will accelerate.
    """
    bid_prices = np.array([b[0] for b in bids])
    ask_prices = np.array([a[0] for a in asks])
    
    # Calculate gaps between 50 levels
    bid_gaps = np.diff(bid_prices)
    if np.max(np.abs(bid_gaps)) > 2.0: # Significant gap detected
        return "VACUUM_LONG"
    return "STABLE"

def get_shannon_entropy(volumes):
    """
    Physics: Entropy measures the randomness of orders. 
    Low entropy = Institutional 'Informed' Flow.
    """
    pk = volumes / np.sum(volumes)
    return -np.sum(pk * np.log2(pk))
