# Analysis of TCP Congestion Control Algorithms

## 1. TCP CUBIC (Loss-based)
### Algorithm Details
- Developed as an improvement over BIC-TCP
- Uses a cubic function for window growth
- Window size (W) is calculated as:
  ```
  W(t) = C(t-K)³ + W_max
  ```
  where:
  - C is a scaling factor
  - t is the elapsed time since last congestion event
  - K is the time period to reach W_max
  - W_max is the window size where the last packet loss occurred

- Features three distinct phases:
  1. Fast convergence during initial growth
  2. Steady-state around W_max
  3. Exploratory phase for available bandwidth

### Suitable Scenarios and Limitations
#### Best Used For:
- High-speed, long-distance networks (High BDP networks)
- Networks with large bandwidth variations
- Data centers and cloud environments
- Bulk data transfer applications

#### Limitations:
- Can be aggressive in competing with other TCP flows
- May not perform optimally in wireless networks with random losses
- Performance degrades in networks with frequent random packet losses

## 2. TCP Vegas (Delay-based)
### Algorithm Details
- Uses RTT measurements to detect congestion before packet loss occurs
- Maintains two thresholds: α (minimum) and β (maximum)
- Calculates expected and actual rates:
  - Expected = WindowSize/BaseRTT
  - Actual = WindowSize/CurrentRTT
- Adjusts window based on difference (diff) between rates:
  ```
  if diff < α: increase window linearly
  if diff > β: decrease window linearly
  if α < diff < β: maintain window
  ```

### Suitable Scenarios and Limitations
#### Best Used For:
- Networks with stable RTT
- Interactive applications requiring low latency
- Networks where packet loss is not primarily due to congestion

#### Limitations:
- Performs poorly when competing with loss-based TCP variants
- Sensitive to RTT measurements accuracy
- Not suitable for wireless networks with varying delays

## 3. TCP Veno (Hybrid)
### Algorithm Details
- Combines Vegas's delay-based approach with Reno's loss-based algorithm
- Uses Vegas's method to estimate network congestion state
- Modifies Reno's additive increase mechanism based on estimated state
- Introduces state differentiation:
  ```
  if N < β: State = non-congested
  if N ≥ β: State = congested
  ```
  where N is the number of backlogged packets

### Suitable Scenarios and Limitations
#### Best Used For:
- Wireless networks with random packet losses
- Networks with mixed wired/wireless segments
- Environments requiring balance between throughput and fairness

#### Limitations:
- Complex parameter tuning needed for optimal performance
- May not perform as well as specialized wireless TCP variants
- Can be conservative in high-speed networks

## 4. TCP NewReno (Loss-based)
### Algorithm Details
- Enhancement of TCP Reno with improved fast recovery
- Uses four phases:
  1. Slow Start
  2. Congestion Avoidance
  3. Fast Retransmit
  4. Fast Recovery with multiple packet loss handling
- Maintains a "pipe" variable to estimate packets in flight during recovery

### Suitable Scenarios and Limitations
#### Best Used For:
- Traditional internet environments
- Networks with occasional packet loss
- Applications requiring stable, reliable performance

#### Limitations:
- Not optimal for high-speed networks
- Recovery time can be slow with multiple packet losses
- Performs poorly in wireless environments

## Comparative Analysis

### Performance Metrics Comparison

| Algorithm  | Throughput | Fairness | Stability | RTT Sensitivity |
|------------|------------|----------|-----------|-----------------|
| CUBIC      | High       | Moderate | Good      | Low            |
| Vegas      | Moderate   | High     | Excellent | High           |
| Veno       | Moderate   | Good     | Good      | Moderate       |
| NewReno    | Moderate   | High     | Good      | Low            |

### Key Inferences

1. **Algorithm Characteristics**
   - CUBIC excels in high-speed networks but can be aggressive
   - Vegas provides excellent stability but struggles with competition
   - Veno offers good balance for wireless networks
   - NewReno provides reliable but conservative performance

2. **Use Case Optimization**
   - High-speed networks: CUBIC
   - Low latency requirements: Vegas
   - Wireless networks: Veno
   - General internet: NewReno

3. **Evolution Pattern**
   - Trend shows movement from pure loss-based to hybrid approaches
   - Increased focus on handling diverse network conditions
   - Growing importance of RTT-based congestion detection

4. **Trade-offs**
   - Higher throughput often comes at cost of fairness
   - Better stability usually means more conservative growth
   - More complex algorithms require more parameter tuning

### References
1. Ha, S., Rhee, I., & Xu, L. (2008). CUBIC: A New TCP-Friendly High-Speed TCP Variant
2. Brakmo, L. S., & Peterson, L. L. (1995). TCP Vegas: End to End Congestion Avoidance on a Global Internet
3. Fu, C. P., & Liew, S. C. (2003). TCP Veno: TCP Enhancement for Transmission Over Wireless Access Networks
4. Floyd, S., & Henderson, T. (1999). The NewReno Modification to TCP's Fast Recovery Algorithm