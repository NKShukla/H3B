# H3B Dataset: HTTP/3 supported Browser Dataset
<a name="readme-top"></a>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ul>
    <li>
      <a href="#experimentalsetup">Experimental Setup</a>
    </li>
    <li>
      <a href="#">Retrieving QoE Parameters from Application Logs</a>
    </li>
  </ul>
</details>

## Retrieving QoE Parameters from Application Logs

This section provides step-by-step instructions on how to use the application logs to retrieve QoE (Quality of Experience) parameters such as bitrate, avg_bitrate, avg_bitrate_variation, and avg_stall. Follow the steps below:

1. Create the following folder hierarchy:
```
.
├── ...
├── data
│ ├── logFiles
│ │ └── slot
│ │ │ └── dynamic-very-low
│ │ │ │ ├── tcp
│ │ │ │ ├── quic
│ ├── jsonFiles
│ │ └── slot
│ │ │ └── dynamic-very-low
│ │ │ │ ├── tcp
│ │ │ │ ├── quic
│ └── csvFiles
│ │ └── slot
│ │ │ └── 64-256-64-inc
│ │ │ │ ├── tcp_qoe
│ │ │ │ ├── quic_qoe
└── ...
```

2. Place the application logs in the **logFiles** folder and organise them between **tcp** and **quic** folders.

3. Open the terminal and run the following command which will generate **tcp** and **quic** files inside the **jsonFiles** folder. 
```
.\create_graphs_slot.bat
```

4. Run the following command in the terminal which will generate both **tcp** and **quic** QoE files under the **csvFiles** folder. 
```
.\scripts\get_json.py slot dynamic-very-low
```

**NOTE:** We have added both **tcp** and **quic** QoE files inside the **application-logs-qoe** collected over 5 geographical locations under **dynamic-high**, **dynamic-low** and **dynamic-very-low**. 

Make sure to follow these steps to effectively retrieve the QoE parameters from the application logs.