# <span id="page-261-0"></span>5.0 CXL ARB/MUX

<span id="page-261-2"></span>[Figure 5-1](#page-261-1) shows where the CXL ARB/MUX exists in the Flex Bus layered hierarchy. The ARB/MUX provides dynamic muxing of the CXL.io and CXL.cachemem link layer control and data signals to interface with the Flex Bus physical layer.

<span id="page-261-1"></span>**Figure 5-1. Flex Bus Layers - CXL ARB/MUX Highlighted**

![](_page_261_Figure_5.jpeg)

In the transmit direction, the ARB/MUX arbitrates between requests from the CXL link layers and multiplexes the data. It also processes power state transition requests from the link layers: resolving them to a single request to forward to the physical layer, maintaining virtual link state machines (vLSMs) for each link layer interface, and generating ARB/MUX link management packets (ALMPs) to communicate the power state transition requests across the link on behalf of each link layer. See [Section 10.3,](#page-883-3) [Section 10.4,](#page-889-4) and [Section 10.5](#page-890-3) for more details on how the ALMPs are utilized in the overall flow for power state transitions. In PCIe\* mode, the ARB/MUX is bypassed, and thus ALMP generation by the ARB/MUX is disabled.

In the receive direction, the ARB/MUX determines the protocol associated with the CXL flit and forwards the flit to the appropriate link layer. It also processes the ALMPs, participating in any required handshakes and updating its vLSMs as appropriate.

For 256B Flit mode, the replay buffer is part of the Physical Layer. ALMPs have a different flit format than in 68B Flit mode, and are protected by forward error correction (FEC) and cyclic redundancy check (CRC). They must also be allocated to the replay buffer in the Physical Layer and follow the replay sequence protocols. Hence, they are guaranteed to be delivered to the remote ARB/MUX error free.

## <span id="page-262-0"></span>5.1 vLSM States

The ARB/MUX maintains vLSMs for each CXL link layer it interfaces with, transitioning the state based on power state transition requests it receives from the local link layer or from the remote ARB/MUX on behalf of a remote link layer. [Table 5-1](#page-262-1) lists the different possible states for the vLSMs. PM States and Retrain are virtual states that can differ across interfaces (CXL.io, CXL.cache, and CXL.mem); however, all other states such as LinkReset, LinkDisable, and LinkError are forwarded to the Link Layer and are therefore synchronized across interfaces.

<span id="page-262-1"></span>**Table 5-1. vLSM States Maintained per Link Layer Interface**

| vLSM State                                                                                                                                                                                                                         | Description                                                                                                                                                    |  |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| Reset                                                                                                                                                                                                                              | Power-on default state during which initialization occurs                                                                                                      |  |
| Active                                                                                                                                                                                                                             | Normal operational state                                                                                                                                       |  |
| Substate of Active to indicate unsuccessful ALMP negotiation of PM entry. This is not a state<br>Active.PMNAK<br>requested by the Link Layer. It is applicable only for Upstream Ports. It is not applicable for 68B Flit<br>mode. |                                                                                                                                                                |  |
| L1.0                                                                                                                                                                                                                               | Power savings state, from which the link can enter Active via Retrain (maps to PCIe L1)                                                                        |  |
| L1.1                                                                                                                                                                                                                               | Power savings state, from which the link can enter Active via Retrain (reserved for future use)                                                                |  |
| L1.2                                                                                                                                                                                                                               | Power savings state, from which the link can enter Active via Retrain (reserved for future use)                                                                |  |
| L1.3                                                                                                                                                                                                                               | Power savings state, from which the link can enter Active via Retrain (reserved for future use)                                                                |  |
| DAPM                                                                                                                                                                                                                               | Deepest Allowable PM State (not a resolved state; a request that resolves to an L1 substate)                                                                   |  |
| SLEEP_L2                                                                                                                                                                                                                           | Power savings state, from which the link must go through Reset to reach Active                                                                                 |  |
| LinkReset                                                                                                                                                                                                                          | Reset propagation state resulting from software-initiated or hardware-initiated reset                                                                          |  |
| LinkError                                                                                                                                                                                                                          | Link Error state due to hardware-detected errors that cannot be corrected through link recovery<br>(e.g., uncorrectable internal errors or surprise link down) |  |
| LinkDisable                                                                                                                                                                                                                        | Software-controlled link disable state                                                                                                                         |  |
| Retrain<br>Transitory state that transitions to Active                                                                                                                                                                             |                                                                                                                                                                |  |

*Note:* When the Physical Layer LTSSM enters Hot Reset or Disabled state, that state is communicated to all link layers as LinkReset or LinkDisable, respectively. No ALMPs are exchanged, regardless of who requested them, for these transitions. LinkError must take the LTSSM to Detect or Disabled. For example, it is permitted to map CXL.io Downstream Port Containment to LinkError (when the LTSSM is in Disabled state).

The ARB/MUX looks at the state of each vLSM to resolve to a single state request to forward to the physical layer as specified in Table 5-2. For example, if the current vLSM[0] state is L1.0 (row = L1.0) and the current vLSM[1] state is Active (column = Active), then the resolved request from the ARB/MUX to the Physical layer will be Active.

<span id="page-263-0"></span>Table 5-2. ARB/MUX Multiple vLSM Resolution Table

| Resolved Request from ARB/MUX<br>to Flex Bus Physical Layer<br>(Row = current vLSM[0] state;<br>Column = current vLSM[1] state) | Reset            | Active | L1.0   | L1.1<br>(reserved<br>for future<br>use) | L1.2<br>(reserved<br>for future<br>use) | L1.3<br>(reserved<br>for future<br>use) | SLEEP_L2      |
|---------------------------------------------------------------------------------------------------------------------------------|------------------|--------|--------|-----------------------------------------|-----------------------------------------|-----------------------------------------|---------------|
| Reset                                                                                                                           | RESET            | Active | L1.0   | L1.1 or<br>lower                        | L1.2 or<br>lower                        | L1.3 or<br>lower                        | SLEEP_L2      |
| Active                                                                                                                          | Active           | Active | Active | Active                                  | Active                                  | Active                                  | Active        |
| L1.0                                                                                                                            | L1.0             | Active | L1.0   | L1.0                                    | L1.0                                    | L1.0                                    | L1.0          |
| L1.1 (reserved for future use)                                                                                                  | L1.1 or<br>lower | Active | L1.0   | L1.1 or<br>lower                        | L1.1 or<br>lower                        | L1.1 or<br>lower                        | L1.1 or lower |
| L1.2 (reserved for future use)                                                                                                  | L1.2 or<br>lower | Active | L1.0   | L1.1 or<br>lower                        | L1.2 or<br>lower                        | L1.2 or<br>lower                        | L1.2 or lower |
| L1.3 (reserved for future use)                                                                                                  | L1.3 or<br>lower | Active | L1.0   | L1.1 or<br>lower                        | L1.2 or<br>lower                        | L1.3 or<br>lower                        | L1.3 or lower |
| SLEEP_L2                                                                                                                        | SLEEP_L2         | Active | L1.0   | L1.1 or<br>lower                        | L1.2 or<br>lower                        | L1.3 or<br>lower                        | SLEEP_L2      |

Based on the requested state from one or more of the Link Layers, ARB/MUX will change the state request to the physical layer for the desired link state.

For implementations in which the Link Layers support directing the ARB/MUX to LinkReset or LinkError or LinkDisable, the ARB/MUX must unconditionally propagate these requests from the requesting Link Layer to the Physical Layer; this takes priority over Table 5-2.

Table 5-3 describes the conditions under which a vLSM transitions from one state to the next. A transition to the next state occurs after all the steps in the trigger conditions column are complete. Some of the trigger conditions are sequential and indicate a series of actions from multiple sources. For example, on the transition from Active to L1.x state on an Upstream Port, the state transition will not occur until the vLSM has received a request to enter L1.x from the Link Layer followed by the vLSM sending a Request ALMP{L1.x} to the remote vLSM. Next, the vLSM must wait to receive a Status ALMP{L1.x} from the remote vLSM. Once all these conditions are met in sequence, the vLSM will transition to the L1.x state as requested. Certain trigger conditions are applicable only when operating in 68B Flit mode, and these are highlighted in the table "For 68B Flit mode only".

Evaluation Copy

<span id="page-264-1"></span><span id="page-264-0"></span>**Table 5-3. ARB/MUX State Transition Table (Sheet 1 of 2)**

| Current vLSM State                 | Next State   | Upstream Port Trigger Condition                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Downstream Port Trigger Condition                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
|------------------------------------|--------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                                    | L1.x         | Upon receiving a Request to enter L1.x<br>from Link Layer, the ARB/MUX must<br>initiate a Request ALMP{L1.x} and<br>receive a Status ALMP{L1.x} from the<br>remote vLSM                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Upon receiving a Request to enter L1.x<br>from Link Layer and receiving a<br>Request ALMP{L1.x} from the Remote<br>vLSM, the ARB/MUX must send Status<br>ALMP{L1.x} to the remote vLSM                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Active                             | L2           | Upon receiving a Request to enter L2<br>from Link Layer the ARB/MUX must<br>initiate a Request ALMP{L2} and<br>receive a Status ALMP{L2} from the<br>remote vLSM                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Upon receiving a Request to enter L2<br>from Link Layer and receiving a<br>Request ALMP{L2} from the Remote<br>vLSM the ARB/MUX must send Status<br>ALMP{L2} to the remote vLSM                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
|                                    | Active.PMNAK | For 256B Flit mode: Upon receiving a<br>PMNAK ALMP from the Downstream<br>Port ARB/MUX.<br>This arc is not applicable for 68B Flit<br>mode.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Active.PMNAK                       | Active       | For 256B Flit mode: Upon receiving a<br>request to enter Active from the Link<br>Layer (see Section 5.1.2.4.2.2).<br>This arc is not applicable for 68B Flit<br>mode.                                                                                                                                                                                                                                                                                                                                                                                                                                                               | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| L1.x                               | Retrain      | Upon receiving an ALMP Active request<br>from remote ARB/MUX                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Upon receiving an ALMP Active request<br>from remote ARB/MUX                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Active                             | Retrain      | For 68B Flit mode only: Any of the<br>following two conditions are met:<br>1) Physical Layer LTSSM enters<br>Recovery.<br>2) Physical Layer transitions from<br>Recovery to L0 and State Status ALMP<br>synchronization for Recovery exit<br>resolves to Retrain (see<br>Section 5.1.2.3).<br>For 256B Flit mode, this arc is not<br>applicable since the replay buffer is<br>moved to logPHY, there is no reason to<br>expose Active to Retrain arc to protocol<br>layer vLSMs.                                                                                                                                                    | For 68B Flit mode only: Physical Layer<br>LTSSM enters Recovery.<br>For 256B Flit mode, this arc is not<br>applicable since the replay buffer is<br>moved to logPHY, there is no reason to<br>expose Active to Retrain arc to protocol<br>layer vLSMs.                                                                                                                                                                                                                                                                                                                                                                              |
| Retrain                            | Active       | Link Layer is requesting Active and any<br>of the following conditions are met:<br>1) For 68B Flit mode only: Physical<br>Layer transitions from Recovery to L0<br>and State Status ALMP synchronization<br>for Recovery exit resolves to Active.<br>2) For 68B Flit mode only: Physical<br>Layer transitions from Recovery to L0<br>and State Status ALMP synchronization<br>for Recovery exit does not resolve to<br>Active. Entry to Active ALMP exchange<br>protocol is complete (see<br>Section 5.1.2.2).<br>3) Physical Layer has been in L0. Entry<br>to Active ALMP exchange protocol is<br>complete (see Section 5.1.2.2). | Link Layer is requesting Active and any<br>of the following conditions are met:<br>1) For 68B Flit mode only: Physical<br>Layer transitions from Recovery to L0<br>and State Status ALMP synchronization<br>for Recovery exit resolves to Active.<br>2) For 68B Flit mode only: Physical<br>Layer transitions from Recovery to L0<br>and State Status ALMP synchronization<br>for Recovery exit does not resolve to<br>Active. Entry to Active ALMP exchange<br>protocol is complete (see<br>Section 5.1.2.2).<br>3) Physical Layer has been in L0. Entry<br>to Active ALMP exchange protocol is<br>complete (see Section 5.1.2.2). |
| Retrain                            | Reset        | For 68B Flit mode: Physical Layer<br>transitions from Recovery to L0 and<br>State Status ALMP synchronization for<br>Recovery exit resolves to Reset (see<br>Section 5.1.2.3).<br>For 256B Flit mode, this arc is N/A.                                                                                                                                                                                                                                                                                                                                                                                                              | N/A                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ANY (Except Disable/<br>LinkError) | LinkReset    | Physical Layer LTSSM in Hot Reset                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Physical Layer LTSSM in Hot Reset                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

**Table 5-3. ARB/MUX State Transition Table (Sheet 2 of 2)**

|  | Current vLSM State<br>Next State<br>ANY (Except LinkError)<br>Disabled |        | Upstream Port Trigger Condition                                                                                                                                                                                                                                                                                                                               | Downstream Port Trigger Condition                                                                                                                                                                                                                                                                                                                             |  |
|--|------------------------------------------------------------------------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
|  |                                                                        |        | Physical Layer LTSSM in Disabled state                                                                                                                                                                                                                                                                                                                        | Physical Layer LTSSM in Disabled state                                                                                                                                                                                                                                                                                                                        |  |
|  | ANY<br>LinkError                                                       |        | Directed to enter LinkError from Link<br>Layer or indication of LinkError from<br>Physical Layer                                                                                                                                                                                                                                                              | Directed to enter LinkError from Link<br>Layer or indication of LinkError from<br>Physical Layer                                                                                                                                                                                                                                                              |  |
|  | L2                                                                     | Reset  | Implementation Specific. Refer to rule 3<br>in Section 5.1.1.                                                                                                                                                                                                                                                                                                 | Implementation Specific. Refer to rule 3<br>in Section 5.1.1.                                                                                                                                                                                                                                                                                                 |  |
|  | Disabled<br>Reset<br>LinkError<br>Reset<br>LinkReset<br>Reset          |        | Implementation Specific. Refer to rule 3<br>in Section 5.1.1.                                                                                                                                                                                                                                                                                                 | Implementation Specific. Refer to rule 3<br>in Section 5.1.1.                                                                                                                                                                                                                                                                                                 |  |
|  |                                                                        |        | Implementation Specific. Refer to rule 3<br>in Section 5.1.1.                                                                                                                                                                                                                                                                                                 | Implementation Specific. Refer to rule 3<br>in Section 5.1.1.                                                                                                                                                                                                                                                                                                 |  |
|  |                                                                        |        | Implementation Specific. Refer to rule 3<br>in Section 5.1.1.                                                                                                                                                                                                                                                                                                 | Implementation Specific. Refer to rule 3<br>in Section 5.1.1.                                                                                                                                                                                                                                                                                                 |  |
|  | Reset                                                                  | Active | Any of the following conditions are met:<br>1) Link Layer is asking for Active and<br>Entry to Active ALMP exchange protocol<br>is complete (see Section 5.1.2.2).<br>2) For 68B Flit mode only: Physical<br>Layer transitions from Recovery to L0<br>and State Status ALMP synchronization<br>for Recovery exit resolves to Active (see<br>Section 5.1.2.3). | Any of the following conditions are met:<br>1) Link Layer is asking for Active and<br>Entry to Active ALMP exchange protocol<br>is complete (see Section 5.1.2.2).<br>2) For 68B Flit mode only: Physical<br>Layer transitions from Recovery to L0<br>and State Status ALMP synchronization<br>for Recovery exit resolves to Active (see<br>Section 5.1.2.3). |  |

### <span id="page-265-0"></span>5.1.1 Additional Rules for Local vLSM Transitions

1. For 68B Flit mode, if any Link Layer requests entry into Retrain to the ARB/MUX, the ARB/MUX must forward the request to the Physical Layer to initiate LTSSM transition to Recovery. In accordance with the Active to Retrain transition trigger condition, after the LTSSM is in Recovery, the ARB/MUX should reflect Retrain to all vLSMs that are in Active state. For 256B Flit mode, there is no Active to Retrain arc in the ARB/MUX vLSM because Physical Layer LTSSM transitions to Recovery do not impact vLSM state.

**Figure 5-2. Entry to Active begins with**

*Note:* For 256B Flit mode: Not exposing the Physical Layer LTSSM transition to Recovery to the Link Layer vLSMs allows for optimizations in which the Rx Retry buffer can drain while the LTSSM is in Recovery. It also avoids corner cases in which the vLSMs become out of sync with the remote Link partner. To handle error conditions such as UpdateFC DLLP timeouts, implementations must have a sideband mechanism from the Link Layers to the Physical Layer for triggering the LTSSM transition to Recovery.

- 2. Once a vLSM is in Retrain state, it is expected that the corresponding Link Layer will eventually request ARB/MUX for a transition to Active.
<span id="page-265-4"></span><span id="page-265-3"></span>- 3. If the LTSSM moves to Detect, each vLSM must eventually transition to Reset.

### <span id="page-265-1"></span>5.1.2 Rules for vLSM State Transitions across Link

This section refers to vLSM state transitions.

#### <span id="page-265-2"></span>5.1.2.1 General Rules

• The link cannot operate for any other protocols if the CXL.io protocol is down (CXL.io operation is a minimum requirement)

#### <span id="page-266-0"></span>5.1.2.2 Entry to Active Exchange Protocol

The ALMP protocol required for the entry to active consists of 4 ALMP exchanges between the local and remote vLSMs as seen in Figure 5-2. Entry to Active begins with an Active State Request ALMP sent to the remote vLSM which responds with an Active State Status ALMP. The only valid response to an Active State Request is an Active State Status once the corresponding Link Layer is ready to receive protocol flits. The remote vLSM must also send an Active State Request ALMP to the local vLSM which responds with an Active State Status ALMP.

During initial link training, the Upstream Port (UP in Figure 5-2) must wait for a non-physical layer flit (i.e., a flit that was not generated by the physical layer of the Downstream Port (DP in Figure 5-2)) before transmitting any ALMPs (see Section 6.4.1). Thus, during initial link training, the first ALMP is always sent from the Downstream Port to the Upstream Port. If additional Active exchange handshakes subsequently occur (e.g., as part of PM exit), the Active request ALMP can be initiated from either side.

Once an Active State Status ALMP has been sent and received by a vLSM, the vLSM transitions to Active State.

<span id="page-266-2"></span>Figure 5-2. Entry to Active Protocol Exchange

![](_page_266_Figure_7.jpeg)

#### <span id="page-266-1"></span>5.1.2.3 Status Synchronization Protocol

For 256B Flit mode, since the retry buffer is in the physical layer, all ALMPs are guaranteed to be delivered error free to the remote ARB/MUX. Additionally, all ALMPs are guaranteed to get a response. Therefore, there is no scenario where the Upstream Port and Downstream Port vLSMs can get out of sync.
**Figure 5-16. Snapshot Example during Status Synchronization**


Status Synchronization Protocol is only applicable for 68B Flit mode. The following description and rules are applicable for 68B Flit mode.

After the highest negotiated speed of operation is reached during initial link training, all subsequent LTSSM Recovery transitions must be signaled to the ARB/MUX. vLSM Status Synchronization Protocol must be performed after Recovery exit. A Link Layer cannot conduct any other communication on the link coming out of LTSSM recovery until Status Synchronization Protocol is complete for the corresponding vLSM. Figure 5-3 shows an example of Status Synchronization Protocol.

The Status Synchronization Protocol completion requires the following events in the order listed:

- 1. Status Exchange: Transmit a State Status ALMP, and receive an error free State Status ALMP. The state indicated in the transmitted State Status ALMP is a snapshot of the vLSM state. Refer to Section 5.1.2.3.1.
- 2. A corresponding State Status Resolution based on the sent and received State Status ALMPs during the synchronization exchange. See Table 5-4 for determining the resolved vLSM state.
- 3. New State Request and Status ALMP exchanges when applicable. This occurs if the resolved vLSM state is not the same as the Link Layer requested state.

##### <span id="page-267-2"></span>5.1.2.3.1 vLSM Snapshot Rule

A STATUS\_EXCHANGE\_PENDING variable is used to determine when a snapshot of the vLSM can be taken. The following rules apply:

- Snapshot of the vLSM is taken before entry to LTSSM Recovery if the STATUS EXCHANGE PENDING variable is cleared for that vLSM
- STATUS\_EXCHANGE\_PENDING variable is set for a vLSM once a snapshot is taken
- STATUS\_EXCHANGE\_PENDING variable is cleared on reset or on completion of Status Exchange (i.e., Transmit a State Status ALMP, and receive an error free State Status ALMP)

This is to account for situations where a corrupted State Status ALMP during Status Exchange can lead to additional LTSSM transitions through Recovery. See Figure 5-16 for an example of this flow.

<span id="page-267-0"></span>**Figure 5-3. Example Status Exchange**

![](_page_267_Figure_12.jpeg)

<span id="page-267-1"></span>Table 5-4. vLSM State Resolution after Status Exchange (Sheet 1 of 2)

| No. | Sent Status ALMP | Received Status ALMP | Resolved vLSM State |
|-----|------------------|----------------------|---------------------|
| 1.  | Reset            | Reset                | Reset               |
| 2.  | Reset            | Active               | Active              |
| 3.  | Reset            | L2                   | Reset               |
| 4.  | Active           | Reset                | Active              |
| 5.  | Active           | Active               | Active              |
| 6.  | Active           | Retrain              | Active              |
| 7.  | Active           | L1.x                 | Retrain             |
| 8.  | Active           | L2                   | Reset               |

**Table 5-4. vLSM State Resolution after Status Exchange (Sheet 2 of 2)**

| No. | Sent Status ALMP | Received Status ALMP | Resolved vLSM State |
|-----|------------------|----------------------|---------------------|
| 9.  | Retrain          | Active               | Active              |
| 10. | Retrain          | Retrain              | Retrain             |
| 11. | Retrain          | L1.x                 | Retrain             |
| 12. | L1.x             | Active               | L1.x                |
| 13. | L1.x             | Retrain              | L1.x                |
| 14. | L1.x             | L1.x                 | L1.x                |
| 15. | L2               | Active               | L2                  |
| 16. | L2               | Reset                | L2                  |
| 17. | L2               | L2                   | L2                  |

**Figure 5-4.**

##### 5.1.2.3.2 Notes on State Resolution after Status Exchange ([Table 5-4](#page-267-1))

- For the rows where the resolved state is Active, the corresponding ARB/MUX must ensure that protocol flits received immediately after the State Status ALMP from remote ARB/MUX can be serviced by the Link Layer of the corresponding vLSM. One way to guarantee this is to ensure that for these cases the Link Layer receiver is ready before sending the State Status ALMP during Status Exchange.
- Rows 7 and 11 will result in L1 exit flow following state resolution. The corresponding ARB/MUX must initiate a transition to Active through new State Request ALMPs. Once both the Upstream Port VLSM and Downstream Port vLSM are in Active, the Link Layers can redo PM entry negotiation if required. Similarly, for row 10 if reached during PM negotiation, it is required for both vLSMs to initiate Active request ALMPs.
- When supported, rows 3 and 8 will result in L2 exit flow following state resolution. Since the LTSSM will eventually move to Detect, each vLSM will eventually transition to Reset state.
- Rows 7 and 8 are applicable only for Upstream Ports. Since entry into PM is always initiated by the Upstream Port, and it cannot transition its vLSM to PM unless the Downstream Port has done so, there is no case where these rows can apply for Downstream Ports.
- Behavior is undefined and implementation specific for combinations not captured in [Table 5-4.](#page-267-1)

#### <span id="page-268-0"></span>5.1.2.4 State Request ALMP

The following rules apply for sending a State Request ALMP. A State Request ALMP is sent to request a state change to Active or PM. For PM, the request can only be initiated by the ARB/MUX on the Upstream Port.

##### 5.1.2.4.1 For Entry into Active

- All Recovery state operations must complete before the entry to Active sequence starts. For 68B Flit mode, this includes the completion of Status Synchronization Protocol after LTSSM transitions from Recovery to L0.
- An ALMP State Request is sent to initiate the entry into Active State.
- A vLSM must send a Request and receive a Status before the transmitter is considered active. This is not equivalent to vLSM Active state.
- Protocol layer flits must only be transmitted once the vLSM has reached Active state.

Figure 5-4 shows an example of entry into the Active state. The flows in Figure 5-4 show four independent actions (ALMP handshakes) that may not necessarily occur in the order or small timeframe shown. The vLSM transmitter and receiver may become active independent of one another. Both transmitter and receiver must be active before the vLSM state is Active. The transmitter becomes active after a vLSM has transmitted a Request ALMP{Active} and received a Status ALMP{Active}. The receiver becomes active after a vLSM receives a Request ALMP{Active} and sends a Status ALMP{Active} in response.
**Figure 5-5. CXL Entry to PM State Example**


Please refer to Section 5.1.2.2 for rules regarding the Active State Request/Status handshake protocol.

<span id="page-269-0"></span>Figure 5-4. CXL Entry to Active Example Flow

![](_page_269_Figure_5.jpeg)
**Figure 5-6.**


##### 5.1.2.4.2 For Entry into PM State (L1/L2)

- An ALMP State Request is sent to initiate the entry into PM States. Only Upstream Ports can initiate entry into PM states.
- · For Upstream Ports, a vLSM must send a Request and receive a Status before the PM negotiation is considered complete for the corresponding vLSM.

Figure 5-5 shows an example of Entry to PM State (L1) initiated by the Upstream Port (UP in the figure) ARB/MUX. Each vLSM will be ready to enter L1 State once the vLSM has sent a Request ALMP{L1} and received a Status ALMP{L1} in return or the vLSM has received a Request ALMP{L1} and sent a Status ALMP{L1} in return. The vLSMs operate independently and actions may not complete in the order or within the timeframe shown. Once all vLSMs are ready to enter PM State (L1), the Channel will complete the EIOS exchange and enter L1.

<span id="page-270-0"></span>Figure 5-5. **CXL Entry to PM State Example** 

![](_page_270_Figure_7.jpeg)

###### 5.1.2.4.2.1 PM Retry and Reject Scenarios for 68B Flit Mode

This section is applicable for 68B Flit mode only. If PM entry is not accepted by the Downstream Port, it must not respond to the PM State Request. In this scenario:

• The Upstream Port is permitted to retry entry into PM with another PM State Request after a 1-ms (not including time spent in recovery states) timeout, when waiting for a response for a PM State Request. Upstream Port must not expect a PM State Status response for every PM State Request ALMP. Even if the Upstream Port has sent multiple PM State Requests because of PM retries, if it receives a single PM State Status ALMP, it must move the corresponding vLSM to the PM state indicated in the ALMP. For a Downstream Port, if the vLSM is Active and it has received multiple PM State Request ALMPs for that vLSM, it is permitted to treat the requests as a single PM request and respond with a single PM State Status only if the vLSM transitions into the PM state. Figure 5-6 shows an example of this flow.

<span id="page-271-0"></span>Figure 5-6. Successful PM Entry following PM Retry

**Figure 5-7.**

![](_page_271_Figure_3.jpeg)

- The Upstream Port is also permitted to abort entry into PM by sending an Active State Request ALMP for the corresponding vLSM. Two scenarios are possible in this case:
  - Downstream Port receives the Active State Request before the commit point of PM acceptance. The Downstream Port must abort PM entry and respond with Active State Status ALMP. The Upstream Port can begin flit transfer toward the Downstream Port once Upstream Port receives Active State Status ALMP. Since the vLSMs are already in Active state and flit transfer was already allowed from the Downstream Port to the Upstream Port direction during this flow, there is no Active State Request ALMP from the Downstream Port-to-Upstream Port direction. Figure 5-7 shows an example of this flow.

<span id="page-271-1"></span>Figure 5-7. **PM Abort before Downstream Port PM Acceptance** 

![](_page_271_Figure_7.jpeg)

**Figure 5-9.**

— Downstream Port receives the Active State Request after the commit point of PM acceptance or after its vLSM is in a PM state. The Downstream Port must finish PM entry and send PM State Status ALMP (if not already done so). The Upstream Port must treat the received PM State Status ALMP as an unexpected ALMP and trigger link Recovery. Figure 5-8 shows an example of this flow.

<span id="page-272-0"></span>Figure 5-8. PM Abort after Downstream Port PM Acceptance

**Figure 5-8.**

![](_page_272_Figure_4.jpeg)

###### <span id="page-272-1"></span>5.1.2.4.2.2 PM Retry and Reject Scenario for 256B Flit Mode

<span id="page-272-2"></span>This section is applicable for 256B Flit mode only. Upon receiving a PM Request ALMP, the Downstream Port must respond to it with either a PM Status ALMP or an Active.PMNAK Status ALMP.

It is strongly recommended for the Downstream Port ARB/MUX to send the response ALMP to the Physical Layer within 10 us of receiving the request ALMP from the Physical Layer (the time is counted only during the L0 state of the physical LTSSM, excluding the time spent in the Downstream Port's Rx Retry buffer for the request, or the time spent in the Downstream Port's Tx Retry buffer for the response). If the Downstream Port does not meet the conditions to accept PM entry within that time window, it must respond with an Active.PMNAK Status ALMP.

The Downstream Port ARB/MUX must wait for at least 1 us after receiving the PM Request ALMP from the Physical Layer before deciding whether to schedule an Active.PMNAK Status ALMP.

There is no difference between a PM Request ALMP for PCI-PM vs. ASPM. For both cases on the CXL.io Downstream Port, idle time with respect to lack of TLP flow triggers the Link Layer to request L1 to ARB/MUX. Waiting for at least 1 us on the Downstream Port, the ARB/MUX provides sufficient time for the PCI-PM-related CSR completion from the Upstream Port to the Downstream Port for the write to the non-D0 state to exit the Downstream Port's CXL.io Link Layer, and reduces the likelihood of returning an Active.PMNAK Status ALMP.

Upon receiving an Active.PMNAK Status ALMP, the Upstream Port must transition the corresponding vLSM to Active.PMNAK state. The Upstream port must continue to receive and process flits while the vLSM state is Active or Active.PMNAK. If PMTimeout

Note:

(see Section 8.2.5.1) is enabled and a response is not received for a PM Request ALMP within the programmed time window, the ARB/MUX must treat this as an uncorrectable internal error and escalate accordingly.

For Upstream Ports, after the Link Layer requests PM entry, the Link Layer must not change this request until it observes the vLSM status change to either the requested state or Active.PMNAK or one of the non-virtual states (LinkError, LinkReset, LinkDisable, or Reset). If Active.PMNAK is observed, the Link Layer must request Active to the ARB/MUX and wait for the vLSM to transition to Active before transmitting flits or re-requesting PM entry (if PM entry conditions are met).

The PM handshakes are reset by any events that cause physical layer LTSSM transitions that result in vLSM states of LinkError, LinkReset, LinkDisable, or Reset; these can occur at any time. Because these are Link down events, no response will be received for any outstanding Request ALMPs.

<span id="page-273-1"></span>Figure 5-9. Example of a PMNAK Flow

![](_page_273_Figure_6.jpeg)

#### <span id="page-273-0"></span>5.1.2.5 L0p Support

<span id="page-273-2"></span>256B Flit mode supports LOp as defined in PCIe Base Specification; however, instead of using Link Management DLLPs, the ARB/MUX ALMPs are used to negotiate the LOp width with the Link partner. PCIe rules related to DLLP transmission, corruption, and consequent abandonment of LOp handshakes do not apply to CXL. This section defines the additional rules that are required when ALMPs are used for negotiation of LOp width. See Section 6.9 for information on LOp registers.

When LOp is enabled, the ARB/MUX must aggregate the requested link width indications from the CXL.io and CXL.cachemem Link Layers to determine the LOp width for the physical link. The Link Layers must also indicate to the ARB/MUX whether the LOp request is a priority request (e.g., such as in the case of thermal throttling). The aggregated width must be greater than or equal to the larger link width that is requested by the Link Layers if it is not a priority request. The aggregated width can be greater if the ARB/MUX decides that the two protocol layers combined require a larger width than the width requested by each protocol layer. For example, if CXL.io is requesting a width of x2, and CXL.cachemem is requesting a width of x2, the ARB/MUX is permitted to request and negotiate x4 with the remote Link partner. The specific algorithm for aggregation is implementation specific.

In the case of a priority request from either Link Layer, the aggregated width is the lowest link width that is priority requested by the Link Layers. The ARB/MUX uses LOp ALMP handshakes to negotiate the LOp link width changes with its Link partner.

The following sequence is followed for L0p width changes:

- 1. Each Link Layer indicates its minimum required link width to the ARB/MUX. It also indicates whether the request is a priority request.
- 2. If the ARB/MUX determines that the aggregated L0p width is different from the current width of the physical link, the ARB/MUX must initiate an L0p width change request to the remote ARB/MUX using the L0p request ALMP. It also indicates whether the request is a priority request in the ALMP.
- 3. The ARB/MUX must ensure that there is only one outstanding L0p request at a time to the remote Link partner.
- 4. The ARB/MUX must respond with an L0p ACK or an L0p NAK to any outstanding L0p request ALMP within 1 us. (The time is counted only during the L0 state of the physical LTSSM. Time is measured from the receipt of the request ALMP from the Physical Layer to the scheduling of the response ALMP from the ARB/MUX to the Physical Layer. The time does not include the time spent by the ALMPs in the RX or TX Retry buffers.)
- 5. Whether to send an L0p ACK or an L0p NAK response must be determined using the L0p resolution rules from PCIe Base Specification.
- 6. If PMTimeout (see [Section 8.2.5.1\)](#page-598-2) is enabled and a response is not received for an L0p Request ALMP within the programmed time window, the ARB/MUX must treat this as an uncorrectable internal error and escalate accordingly.
- 7. Once the L0p ALMP handshake is complete, the ARB/MUX must direct the Physical Layer to take the necessary steps for downsizing or upsizing the link, as follows:
  - a. Downsizing: If the ARB/MUX receives an L0p ACK in response to its L0p request to downsize, the ARB/MUX notifies the Physical Layer to start the flow for transitioning to the corresponding L0p width at the earliest opportunity. If the ARB/MUX sends an L0p ACK in response to an L0p request, the ARB/MUX notifies the Physical Layer to participate in the flow for transitioning to the corresponding L0p width once it has been initiated by the remote partner. After a successful L0p width change, the corresponding width must be reflected back to the Link Layers.
  - b. Upsizing: If the ARB/MUX receives an L0p ACK in response to its L0p request to upsize, the ARB/MUX notifies the Physical Layer to immediately begin the upsizing process. If the ARB/MUX sends an L0p ACK in response to an L0p request, the ARB/MUX notifies the Physical Layer of the new width and an indication to wait for upsizing process from the remote Link partner. After a successful L0p width change, the corresponding width must be reflected back to the Link Layers.
**Figure 5-10.**


If the Link has not reached the negotiated L0p width 24 ms after the L0p ACK was sent or received, the ARB/MUX must trigger the Physical Layer to transition the LTSSM to Recovery.

The L0p ALMP handshakes can happen concurrently with vLSM ALMP handshakes. L0p width changes do not affect vLSM states.

In 256B Flit mode, the PCIe-defined PM and Link Management DLLPs are not applicable for CXL.io and must not be used.

Similar to PCIe, the Physical Layer's entry to Recovery or link down conditions restores the link to its maximum configured width and any Physical Layer states related to L0p are reset as if no width change was made. The ARB/MUX must finish any outstanding L0p handshakes before requesting the Physical Layer to enter a PM state. If the ARB/ MUX is waiting for an L0p ACK or NAK from the remote ARB/MUX when the link enters Recovery, after exit from Recovery, the ARB/MUX must continue to wait for the L0p response, discard that response, and then, if desired, reinitiate the L0p handshake.

#### <span id="page-275-0"></span>5.1.2.6 State Status ALMP

##### 5.1.2.6.1 When State Request ALMP Is Received

A State Status ALMP is sent after a valid State Request ALMP is received for Active State (if the current vLSM state is already in Active, or if the current vLSM state is not Active and the request is following the entry into Active protocol) or PM States (when entry to the PM state is accepted). For 68B Flit mode, no State Status ALMP is sent if the PM state is not accepted. For 256B Flit mode, an Active.PMNAK State Status ALMP must be sent if the PM state is not accepted.

##### <span id="page-275-2"></span>5.1.2.6.2 Recovery State (68B Flit Mode Only)

The rules in this section apply only for 68B Flit mode. For 256B Flit mode, physical layer Recovery does not trigger the Status Synchronization protocol.

• The vLSM will trigger link Recovery if a State Status ALMP is received without a State Request first being sent by the vLSM except when the State Status ALMP is received for synchronization purposes (i.e., after the link exits Recovery).

Figure 5-10 shows a general example of Recovery exit. Please refer to Section 5.1.2.3 for details on the status synchronization protocol.

![](_page_275_Figure_9.jpeg)

<span id="page-275-1"></span>Figure 5-10. CXL Recovery Exit Example Flow

On Exit from Recovery, the vLSMs on either side of the channel will send a Status ALMP to synchronize the vLSMs. The Status ALMPs for synchronization may trigger a State Request ALMP if the resolved state and the Link Layer requested state are not the same, as seen in Figure 5-11. Refer to Section 5.1.2.3 for the rules that apply during state synchronization. The ALMP for synchronization may trigger a re-entry to recovery in the case of unexpected ALMPs. This is explained using the example of initial link training flows in Section 5.1.3.1. If the resolved states from both vLSMs are the same as the Link Layer requested state, the vLSMs are considered to be synchronized and will continue normal operation.

**Figure 5-12.**

[Figure 5-11](#page-276-1) shows an example of the exit from a PM State (L1) through Recovery. The Downstream Port (DP in the figure) vLSM[0] in L1 state receives the Active Request, and the link enters Recovery. After the exit from recovery, each vLSM sends Status ALMP{L1} to synchronize the vLSMs. Because the resolved state after synchronization is not equal to the requested state, Request ALMP{Active} and Status ALMP{Active} handshakes are completed to enter Active State.

<span id="page-276-1"></span>**Figure 5-11. CXL Exit from PM State Example**

![](_page_276_Figure_4.jpeg)

#### <span id="page-276-0"></span>5.1.2.7 Unexpected ALMPs (68B Flit Mode Only)

Unexpected ALMPs are applicable only for 68B Flit mode. For 256B Flit mode, there are no scenarios that lead to unexpected ALMPs.

The following situations describe circumstances where an unexpected ALMP will trigger link recovery:

- When performing the Status Synchronization Protocol after exit from recovery, any ALMP other than a Status ALMP is considered an unexpected ALMP and will trigger recovery.
- When an Active Request ALMP has been sent, receipt of any ALMP other than an Active State Status ALMP or an Active Request ALMP is considered an unexpected ALMP and will trigger recovery.
- As outlined in [Section 5.1.2.6.2,](#page-275-2) a State Status ALMP received without a State Request ALMP first being sent is an unexpected ALMP except during the Status Synchronization Protocol.

**Figure 5-13.**

### <span id="page-277-0"></span>5.1.3 Applications of the vLSM State Transition Rules for 68B Flit Mode

#### <span id="page-277-1"></span>5.1.3.1 Initial Link Training

As the link trains from 2.5 GT/s speed to the highest supported speed (8.0 GT/s or higher for CXL), the LTSSM may go through several Recovery to LO to Recovery transitions. Implementations are not required to expose ARB/MUX to all of these Recovery transitions. Depending on whether these initial Recovery transitions are hidden from the ARB/MUX, there are four possible scenarios for the initial ALMP handshakes. In all cases, the vLSM state transition rules guarantee that the situation will resolve itself with the vLSMs reaching Active state. These scenarios are presented in the following figures. Note that the figures are illustrative examples, and implementations must follow the rules outlined in the previous sections. Only one vLSM handshake is shown in the figures, but the similar handshakes can occur for the second vLSM as well. Figure 5-12 shows an example of the scenario where both the Upstream Port and Downstream Port (UP and DP in the figure, respectively) are hiding the initial recovery transitions from ARB/MUX. Since neither of them saw a notification of recovery entry, they proceed with the exchange of Active request and status ALMPs to transition into the Active state. Note that the first ALMP (Active request ALMP) is sent from the Downstream Port to the Upstream Port.

<span id="page-277-2"></span>Figure 5-12. Both Upstream Port and Downstream Port Hide Recovery Transitions from ARB/MUX

![](_page_277_Figure_6.jpeg)

Figure 5-13 shows an example where both the Upstream Port and Downstream Port (UP and DP in the figure, respectively) notify the ARB/MUX of at least one recovery transition during initial link training. In this case, first state status synchronization ALMPs are exchanged (indicating Reset state), followed by regular exchange of Active request and status ALMPs (not explicitly shown). Note that the first ALMP (Reset status) is sent from the Downstream Port to the Upstream Port.

<span id="page-278-0"></span>**Both Upstream Port and Downstream Port Notify ARB/MUX of Recovery Transitions** Figure 5-13.

![](_page_278_Figure_3.jpeg)

Figure 5-14 shows an example of the scenario where the Downstream Port (DP in the figure) hides initial recovery transitions from the ARB/MUX, but the Upstream Port (UP in the figure) does not. In this case, the Downstream Port ARB/MUX has not seen recovery transition, so it begins by sending an Active state request ALMP to the Upstream Port. The Upstream Port interprets this as an unexpected ALMP, which triggers link recovery (which must now be communicated to the ARB/MUX because it is after reaching operation at the highest supported link speed). State status synchronization with state=Reset is performed, followed by regular Active request and status handshakes (not explicitly shown).

<span id="page-279-0"></span>**Figure 5-14. Downstream Port Hides Initial Recovery, Upstream Port Does Not** 

**Figure 5-15.**

![](_page_279_Figure_4.jpeg)

Figure 5-15 shows an example of the scenario where the Upstream Port (UP in the figure) hides initial recovery transitions, but the Downstream Port (DP in the figure) does not. In this case, the Downstream Port first sends a Reset status ALMP. This will cause the Upstream Port to trigger link recovery as a result of the rules in Section 5.1.2.4.2.1 (which must now be communicated to the ARB/MUX because it is after reaching operation at the highest supported link speed). State status synchronization with state=Reset is performed, followed by regular Active request and status handshakes (not explicitly shown).

**Figure 5-17.**

<span id="page-280-1"></span>**Upstream Port Hides Initial Recovery, Downstream Port Does Not Figure 5-15.** 

![](_page_280_Figure_4.jpeg)

#### <span id="page-280-0"></span>5.1.3.2 Status Exchange Snapshot Example

Figure 5-16 shows an example case where a State Status ALMP during Status Exchange gets corrupted for vLSM[1] on the Upstream Port (UP in the figure). A corrupted ALMP is when the lower four DWORDs don't match for a received ALMP; it indicates a bit error on the lower four DWORDs of the ALMP during transmission. The ARB/MUX triggers LTSSM Recovery as a result. When the recovery entry notification is received for the second Recovery entry, the snapshot of vLSM[1] on the Upstream Port is still Active since the status exchanges had not successfully completed.

![](_page_281_Figure_2.jpeg)

<span id="page-281-1"></span>Figure 5-16. Snapshot Example during Status Synchronization

#### <span id="page-281-0"></span>5.1.3.3 L1 Abort Example

Figure 5-17 shows an example of a scenario that could arise during L1 transition of the physical link. It begins with successful L1 entry by both vLSMs through corresponding PM request and status ALMP handshakes. The ARB/MUX even requests the Physical Layer to take the LTSSM to L1 for both the Upstream Port and Downstream Port (UP and DP in Figure 5-17, respectively). However, there is a race and one of the vLSMs requests Active before EIOS is received by the Downstream Port Physical Layer. This causes the ARB/MUX to remove the request for L1 entry (L1 abort), while sending an Active request ALMP to the Upstream Port. When EIOS is eventually received by the physical layer, since the ARB/MUX on the Downstream Port side is not requesting L1 (and there is no support for LOs in CXL), the Physical Layer must take the LTSSM to Recovery to resolve this condition. On Recovery exit, both the Upstream Port and Downstream Port ARB/MUX send their corresponding vLSM state status as part of the synchronization protocol. For vLSM[1], since the resolved state status (Retrain) is not the same as desired state status (Active), another Active request ALMP must be sent by the Downstream Port to the Upstream Port. Similarly, on the Upstream Port side, the received state status (L1) is not the same as the desired state status (Active since the vLSM moving to Retrain will trigger the Upstream Port link layer to request Active), the Upstream Port ARB/MUX will initiate an Active request ALMP to the Downstream Port. After the Active state status ALMP has been sent and received, the corresponding ARB/ MUX will move the vLSM to Active, and the protocol level flit transfer can begin.

<span id="page-282-1"></span>Figure 5-17. L1 Abort Example

![](_page_282_Figure_3.jpeg)

## <span id="page-282-0"></span>5.2 ARB/MUX Link Management Packets

The ARB/MUX uses ALMPs to communicate virtual link state transition requests and responses associated with each link layer to the remote ARB/MUX.

An ALMP is a 1-DWORD packet with the format shown in Figure 5-18. For 68B Flit mode, this 1-DWORD packet is replicated four times on the lower 16 bytes of a 528-bit flit to provide data integrity protection; the flit is zero-padded on the upper bits. If the ARB/MUX detects an error in the ALMP, it initiates a retrain of the link.

<span id="page-282-2"></span>Figure 5-18. ARB/MUX Link Management Packet Format

**Figure 5-18.**

![](_page_282_Figure_8.jpeg)

For 256B Flit mode, Bytes 0, 1, 2, and 3 of the ALMP are placed on Bytes 2, 3, 4, and 5 of the 256B flit, respectively (as defined in Section 6.2.3.1). There is no replication since the ALMP is now protected through CRC and FEC. Figure 5-19 shows the ALMP byte positions in the Standard 256B flit. Figure 5-20 shows the ALMP byte positions in the Latency-Optimized 256B flit. See Section 6.2.3.1 for definitions of the FlitHdr, CRC, and FEC bytes.

<span id="page-283-0"></span>**Figure 5-19. ALMP Byte Positions in Standard 256B Flit**

| FlitHdr<br>(2 bytes) | ALMP<br>Byte 0 | ALMP<br>Byte 1 | ALMP<br>Byte 2 | ALMP<br>Byte 3 | 122 bytes of 00h |  |
|----------------------|----------------|----------------|----------------|----------------|------------------|--|
|                      | 114            | bytes of       | 00h            | CRC (8 bytes)  | FEC (6 bytes)    |  |

<span id="page-283-1"></span>**Figure 5-20. ALMP Byte Positions in Latency-Optimized 256B Flit**

| FlitHdr<br>(2 bytes) | ALMP<br>Byte 0 | ALMP<br>Byte 1 | ALMP<br>Byte 2 | ALMP<br>Byte 3 | 116           | bytes of 00h  | CRC (6 bytes) |
|----------------------|----------------|----------------|----------------|----------------|---------------|---------------|---------------|
| 116 bytes of 00h     |                |                |                |                | FEC (6 bytes) | CRC (6 bytes) |               |

For 256B Flit mode, there are two categories of ALMPs: the vLSM ALMPs and the LOp Negotiation ALMPs. For 68B Flit mode, only vLSM ALMPs are applicable. Byte 1 of the ALMP is shown in Table 5-5.

<span id="page-283-2"></span>**Table 5-5. ALMP Byte 1 Encoding**

| Byte 1 Bits | Description                                                                        |  |  |  |  |
|-------------|------------------------------------------------------------------------------------|--|--|--|--|
|             | Message Encoding                                                                   |  |  |  |  |
| 7:0         | 0000 0001b = L0p Negotiation ALMP (for 256B Flit mode; reserved for 68B Flit mode) |  |  |  |  |
|             | 0000 1000b = vLSM ALMP is encoded in Bytes 2 and 3                                 |  |  |  |  |
|             | All other encodings are reserved                                                   |  |  |  |  |

Bytes 2 and 3 for vLSM ALMPs are shown in [Table 5-6.](#page-284-0) Bytes 2 and 3 for L0p Negotiation ALMPs are shown in [Table 5-7.](#page-284-1)

<span id="page-284-0"></span>**Table 5-6. ALMP Byte 2 and 3 Encodings for vLSM ALMP**

| Byte 2 Bits | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 3:0         | vLSM State Encoding<br>Note: Rx should treat this as reserved for L0p ALMP.<br>•<br>0000b = Reset (for Status ALMP)<br>•<br>0000b = Reserved (for Request ALMP)<br>•<br>0001b = Active<br>•<br>0010b = Reserved (for Request ALMP)<br>•<br>0010b = Active.PMNAK (for Status ALMP for 256B Flit mode; reserved for<br>68B Flit mode)<br>•<br>0011b = DAPM (for Request ALMP)<br>•<br>0011b = Reserved (for Status ALMP)<br>•<br>0100b = IDLE_L1.0 (maps to PCIe L1)<br>•<br>0101b = IDLE_L1.1 (reserved for future use)<br>•<br>0110b = IDLE_L1.2 (reserved for future use)<br>•<br>0111b = IDLE_L1.3 (reserved for future use)<br>•<br>1000b = L2<br>•<br>1011b = Retrain (for Status ALMP only)<br>•<br>1011b = Reserved (for Request ALMP)<br>•<br>All other encodings are reserved |
| 6:4         | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 7           | Request/Status Type<br>•<br>0 = vLSM Status ALMP<br>•<br>1 = vLSM Request ALMP                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Byte 3 Bits | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 3:0         | Virtual LSM Instance Number: Indicates the targeted vLSM interface when<br>there are multiple vLSMs present.<br>•<br>0001b = ALMP for CXL.io<br>•<br>0010b = ALMP for CXL.cache and CXL.mem<br>•<br>All other encodings are reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 7:4         | Reserved                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

<span id="page-284-1"></span>**Table 5-7. ALMP Byte 2 and 3 Encodings for L0p Negotiation ALMP (Sheet 1 of 2)**

| Byte 2 Bits | Description                                                                    |  |  |  |  |
|-------------|--------------------------------------------------------------------------------|--|--|--|--|
| 5:0         | Reserved                                                                       |  |  |  |  |
| 6           | •<br>0 = Not an L0p.Priority Request<br>•<br>1 = L0p.Priority Request          |  |  |  |  |
| 7           | Request/Status Type<br>•<br>0 = L0p Response ALMP<br>•<br>1 = L0p Request ALMP |  |  |  |  |

**Table 5-7. ALMP Byte 2 and 3 Encodings for L0p Negotiation ALMP (Sheet 2 of 2)**

| Byte 3 Bits | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |  |  |  |  |  |  |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|--|--|--|--|
| 3:0         | •<br>0100b = ALMP for L0p (for 256B Flit mode; reserved for 68B Flit mode)<br>•<br>All other encodings are reserved                                                                                                                                                                                                                                                                                                                                                                                                           |  |  |  |  |  |  |
| 7:4         | L0p Width<br>Note: Encodings 0000b to 0100b are requests for L0p Request ALMP, and<br>imply an ACK for L0p Response ALMP.<br>•<br>0000b = x16<br>•<br>0001b = x8<br>•<br>0010b = x4<br>•<br>0011b = x2<br>•<br>0100b = x1<br>•<br>1000b = Reserved for L0p Request ALMP<br>•<br>1000b = L0p NAK for L0p Response ALMP<br>•<br>All other encodings are reserved<br>If the width encoding in an ACK does not match the requested L0p width, the<br>ARB/MUX must consider it a NAK. It is permitted to resend an L0p request, if |  |  |  |  |  |  |

For vLSM ALMPs, the message code used in Byte 1 of the ALMP is 0000 1000b. These ALMPs can be request or status type. The local ARB/MUX initiates transition of a remote vLSM using a request ALMP. After receiving a request ALMP, the local ARB/MUX processes the transition request and returns a status ALMP. For 68B Flit mode, if the transition request is not accepted, a status ALMP is not sent and both local and remote vLSMs remain in their current state. For 256B Flit mode, if the PM transition request is not accepted, an Active.PMNAK Status ALMP is sent.

<span id="page-285-2"></span>For L0p Negotiation ALMPs, the message code used in Byte 1 of the ALMP is 0000 0001b. These ALMPs can be of request or response type. See [Section 5.1.2.5](#page-273-0) for L0p negotiation flow.

### <span id="page-285-0"></span>5.2.1 ARB/MUX Bypass Feature

The ARB/MUX must disable generation of ALMPs when the Flex Bus link is operating in PCIe mode. Determination of the bypass condition can be via hwinit or during link training.

## <span id="page-285-1"></span>5.3 Arbitration and Data Multiplexing/Demultiplexing

The ARB/MUX is responsible for arbitrating between requests from the CXL link layers and multiplexing the data based on the arbitration results. The arbitration policy is implementation specific as long as it satisfies the timing requirements of the higherlevel protocols being transferred over the Flex Bus link. Additionally, there must be a way to program the relative arbitration weightages associated with the CXL.io and CXL.cache + CXL.mem link layers as they arbitrate to transmit traffic over the Flex Bus link. See [Section 8.2.5](#page-598-3) for more details. Interleaving of traffic between different CXL protocols is done at the 528-bit flit boundary for 68B Flit mode, and at the 256B flit boundary for 256B Flit mode.
