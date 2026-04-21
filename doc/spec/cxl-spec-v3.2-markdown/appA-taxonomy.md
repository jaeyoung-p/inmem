# <span id="page-1211-0"></span>Appendix A Taxonomy

<span id="page-1211-3"></span>This appendix was included in the original release of CXL and has not been updated since. It is being included as reference for some original usage and implementation options/ideas for CXL devices. It does not cover features that were added after the initial release, including Back-Invalidate Snoop (BISnp) messages that enable new ways of handling coherence of Host-managed Device Memory (HDM), and new memory device expansion proposals around pooling and Fabric-Attached memory (FAM). See [Chapter 2.0, "CXL System Architecture,"](#page-70-2) for a more-complete set of use cases.

## <span id="page-1211-1"></span>A.1 Accelerator Usage Taxonomy

<span id="page-1211-2"></span>**Table A-1. Accelerator Usage Taxonomy (Sheet 1 of 2)**

| Accelerator Type<br>Description                                                                                                                                                                                                                                                                                                                               |                                                                                                                                                                                                                                                                | Challenges and<br>Opportunities                                                                                                                                                                                                                                                                                        | CXL Support                                                                                           |
|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------|
| Producer-Consumer<br>Accelerators that don't<br>execute against<br>"Memory" without special<br>requirements                                                                                                                                                                                                                                                   | •<br>Works on data streams or large<br>contiguous data objects<br>•<br>Little interaction with the host<br>•<br>Standard P/C ordering model works<br>well                                                                                                      | •<br>Efficient work submission<br>•<br>Efficient exchange of<br>metadata (flow control)                                                                                                                                                                                                                                | •<br>Basic PCIe*<br>•<br>CXL.io                                                                       |
| Producer-Consumer<br>Plus<br>Accelerators that don't<br>execute against<br>"Memory" with special<br>requirements                                                                                                                                                                                                                                              | •<br>Same as above, but…<br>•<br>P/C ordering model doesn't work well<br>•<br>Needs special data operations such<br>as atomics                                                                                                                                 | •<br>Device Coherency can be<br>used to implement varied<br>ordering models and<br>special data operations                                                                                                                                                                                                             | •<br>CXL.cache on CXL<br>with baseline<br>snoop filter<br>support<br>•<br>CXL.io                      |
| •<br>Local memory is often needed for<br>Software-assisted<br>bandwidth or latency predictability<br>SVM Memory<br>•<br>Little interaction with the host<br>Accelerators that execute<br>against "Memory" with<br>•<br>Data management is easily<br>software-supportable<br>implemented in software (e.g., few<br>data management<br>and simple data buffers) |                                                                                                                                                                                                                                                                | •<br>Host software should be<br>able to interact directly<br>with accelerator memory<br>(e.g., SVM, Google, etc.)<br>•<br>Reduces copies,<br>replication, and pinning<br>•<br>Optimizing coherency<br>impact on performance is a<br>challenge<br>•<br>Software can provide best<br>optimization of coherency<br>impact | •<br>CXL Bias model<br>with software<br>managed bias<br>•<br>CXL.io<br>•<br>CXL.cache<br>•<br>CXL.mem |
| Autonomous SVM<br>Memory<br>Accelerators that execute<br>against "Memory" where<br>software-supported data<br>management is<br>impractical                                                                                                                                                                                                                    | •<br>Local memory is often needed for<br>bandwidth or latency predictability<br>•<br>Interaction with the host is common<br>•<br>Data movement is difficult to<br>manage in software (e.g., sparse<br>data structures, pointer-based data<br>structures, etc.) | •<br>Host software should be<br>able to interact directly<br>with accelerator memory<br>(SVM)<br>•<br>Reduces copies,<br>replication, and pinning<br>•<br>Optimizing coherency<br>impact on performance is a<br>challenge<br>•<br>Cannot count on software<br>for bias management                                      | •<br>CXL Bias model<br>with hardware<br>managed bias<br>•<br>CXL.io<br>•<br>CXL.cache<br>•<br>CXL.mem |

**Table A-1. Accelerator Usage Taxonomy (Sheet 2 of 2)**

| Accelerator Type                                                                                                                                                       | Description                                                                                                                                                                                                                                                                                                    | Challenges and<br>Opportunities                                                                                                                                                                     | CXL Support                                                                                                    |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Giant Cache<br>Accelerators that execute<br>against "Memory" where<br>local memory and<br>caching is required                                                          | •<br>Local memory is needed for<br>bandwidth or latency predictability<br>•<br>Data footprint is larger than local<br>memory<br>•<br>Interaction with the host is common<br>•<br>Data must be cycled through<br>accelerator memory in small blocks<br>•<br>Data movement is difficult to<br>manage in software | •<br>Accelerator memory needs<br>to work like a cache (not<br>SVM/system memory)<br>•<br>Ideally, cache misses are<br>detected in hardware, but<br>cache replacements can be<br>managed in software | •<br>CXL.cache on CXL<br>with "Enhanced<br>Directory" snoop<br>filter support<br>•<br>CXL.io<br>•<br>CXL.cache |
| Disaggregated<br>Memory Controller<br>Typically for memory<br>controllers with remote<br>persistent memory,<br>which may be in 2 Level<br>Memory or App Direct<br>mode | •<br>PCIe semantics are needed for<br>device enumeration, driver support,<br>and device management<br>•<br>Most operational flows rely on being<br>able to communicate directly with a<br>Home Device or Near Memory<br>Controller on the Host                                                                 | •<br>Device needs high<br>bandwidth and low-latency<br>path from memory<br>controller to Home Device<br>in the CPU                                                                                  | •<br>CXL.io<br>•<br>CXL.mem                                                                                    |

## <span id="page-1212-0"></span>A.2 Bias Model Flow Example – From CPU

- 1. Start with pages in Device Bias:
  - Pages are guaranteed to not be cached in host cache hierarchy
- 2. Software allocates pages from device memory:
  - a. Software pushes operands to allocated pages from the peer CPU core:
    - For example, Software may use OpenCL\* API to flip operand pages to Host Bias
    - Data copies or cache flushes are not required
  - b. Host CPUs generate operand data in target pages data arrives in an arbitrary location within the host cache hierarchy.
- 3. Device uses operands to generate results:
  - For example, Software may use OpenCL API to flip operand pages back to Device Bias
  - a. API call causes a work descriptor submission to the device descriptor asks the device to flush operand pages from the host cache.
  - b. Cache flush is executed using RdOwnNoData on CXL.cache protocol (see [Table 3-22\)](#page-118-2).
  - c. When Device Bias flip is complete, Software submits work to the accelerator.
  - d. Accelerator executes without any host-related coherency overhead.
  - e. Accelerator dumps data to results pages.
- 4. Software pulls results from the allocated pages:
  - For example, Software uses OpenCL API to flip results pages to Host Bias
  - This action causes some bias states to be changed, but does not cause any coherency or cache-flushing actions
  - Host CPUs can access, cache, and share results data as needed
- 5. Software releases the allocated pages.

OpenCL defines a Coarse-grained buffer Shared Virtual Memory model. Under that model, memory consistency is guaranteed only at explicit synchronization points and these points provide an opportunity to perform bias flip.

Here are some example of OpenCL calls where bias flip can be performed:

- clEnqueueSVMMap provides host access to this buffer. Software may flip the bias from Device bias to Host bias during this call.
- clEnqueueSVMUnmap revokes host access to this buffer. At this point, an OpenCL implementation for a CXL device could flip the bias from Host bias to Device bias.

There are other OpenCL calls where the CPU and the Device share OpenCL buffer objects. Software could flip the bias during those calls.

## <span id="page-1213-0"></span>A.3 CPU Support for Bias Modes

There are two envisaged models of support that the CPU would provide for Bias Modes. These are described below.

### <span id="page-1213-1"></span>A.3.1 Remote Snoop Filter

- Remote socket-owned lines that belong to accelerator-attached memory are tracked by a Remote Snoop-Filter (SF) located in the host CPU Home Agent (HA). Remote SF does not track lines that belong to Host memory. The above removes the need for a directory in device memory. Please note this is only possible in Host Bias mode since in Device Bias mode, local/remote sockets can't cache lines that belong to device memory.
- Local socket-owned lines that belong to accelerator-attached memory will be tracked by a local SF in the host CPU Last Level Cache (LLC) controller. Please note this is only possible in Host Bias mode since in Device Bias mode, local/remote sockets can't cache lines that belong to device memory.
- Device-owned lines that belong to accelerator-attached memory (in Host Bias mode) will NOT be tracked by a local SF in the host CPU LLC controller. These will be tracked by the Device Coherency Engine (DCOH) using a device-specific mechanism (device SF). In Device Bias mode, no coherent tracking is done in the host CPU because the accesses are completed within the device and the host does not see the requests.
- Device-owned lines that belong to host memory (in Host mode or Device mode) will be tracked by a local SF in the host CPU LLC controller. This may cause the device to receive snoops through CXL (CXL.cache) for such lines.

### <span id="page-1213-2"></span>A.3.2 Directory in Accelerator-attached Memory

- Remote socket-owned lines that belong to device memory are tracked by a directory in device memory metadata. The host HA may choose to do broadcast snooping for some cases to avoid reading the metadata.
- Local socket-owned lines that belong to device memory will be tracked by a local SF in the host CPU LLC controller. For access by device, local socket-owned lines that belong to device memory will also update the directory.
- Device-owned lines that belong to device memory will NOT be tracked by a local SF in the host CPU LLC controller. These will be tracked by the Device Coherency Engine (DCOH) using a device-specific mechanism (device SF).
- Device-owned lines that belong to host memory (in Host mode or Device mode) will be tracked by a local SF in the host CPU LLC controller. This may cause the device to receive snoops through CXL (CXL.cache) for such lines.

• Bias Table is located in stolen memory within the device memory and is accessed through the DCOH.

## <span id="page-1214-0"></span>A.4 Giant Cache Model

For problems whose data sets exceed the device-attached memory size, the memory attached to the accelerator needs to be a cache, not memory:

- Typically, the full data set will reside in processor-attached memory
- Subsets of this larger data set are cycled through accelerator memory as the calculation proceeds
- For such use cases, caching is the correct solution:
  - Accelerator memory is not mapped into the system address map data set is built up in host memory
  - Single-page table entry per page in data set no page table manipulation as pages are cycled through accelerator memory
  - Copies of data can be created under driver control and/or hardware control with no OS intervention

<span id="page-1214-1"></span>**Figure A-1. Profile D - Giant Cache Model**

![](_page_1214_Figure_13.jpeg)

Critical issues with a Giant Cache:

- Cache is too large for tracking in the Host on-die SF
- Snoop latency for a Giant Cache is likely to be much higher than standard on-die cache snoop latency

**Recommended CXL solution:**

- Implements SF in processor's coherency directory (stored in DRAM ECC bits), which essentially becomes a highly scalable SF
- Minimizes impact to processor operations that are unrelated to accelerators
- Allows accelerator to access data over CXL.cache as a caching Device
- Provides support on CXL.cache to allow an accelerator to explicitly request directory snoop filtering for Giant Cache
- Processor infrastructure differentiates between low-latency and high-latency requester types
- Support for simultaneous use of a small, low-latency cache associated with the ondie snoop filter is included

**§ §**

![](_page_1215_Picture_1.jpeg)
