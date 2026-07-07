# TON-IoT Dataset

- Source: Official research team OneDrive
- License: [check the ReadMe.pdf you opened — note it here]
- Files used: Modbus, Thermostat, Weather, Network (from Train_Test_datasets/IoT and /Network)
- Format: CSV
- Attack types observed: injection, ddos, backdoor (more to confirm after profiling)
- Label columns: `label` (binary), `type` (multi-class attack name)
- Industrial relevance: Modbus file contains real Modbus function-code fields (FC1–FC4), directly comparable to PLC traffic

Phase - 2 CMD Status
import pandas as pd
>>> df=pd.read_csv(r"D:\datasets\raw\ton_iot\Train_Test_IoT_Mod\bus.csv")
>>> print(df.shape)
(31106, 8)
>>> print(df.columns.tolist())
['date', 'time', 'FC1_Read_Input_Register', 'FC2_Read_Discrete_Value', 'FC3_Read_Holding_Register', 'FC4_Read_Coil', 'label', 'type']
>>> print(df.head())
        date        time  ...  label       type
0  25-Apr-19   09:14:00   ...      1  injection
1  25-Apr-19   09:14:00   ...      1  injection
2  25-Apr-19   09:14:01   ...      1  injection
3  25-Apr-19   09:14:02   ...      1  injection
4  25-Apr-19   09:14:04   ...      1  injection

[5 rows x 8 columns]
>>> import pandas as pd
>>> df=pd.read_csv(r"D:\datasets\raw\ton_iot\Train_Test_IoT_The\rmostat.csv")
>>> print(df.shape)
(32774, 6)
>>> print(df.columns.tolist())
['date', 'time', 'current_temperature', 'thermostat_status', 'label', 'type']
>>> print(df.head())
        date     time  ...  label       type
0  25-Apr-19  8:59:02  ...      1  injection
1  25-Apr-19  8:59:06  ...      1  injection
2  25-Apr-19  8:59:06  ...      1  injection
3  25-Apr-19  8:59:06  ...      1  injection
4  25-Apr-19  8:59:06  ...      1  injection

[5 rows x 6 columns]
>>> import pandas as pd
>>> df=pd.read_csv(r"D:\datasets\raw\ton_iot\Train_Test_IoT_Wea\ther.csv")
>>> print(df.shape)
(39260, 7)
>>> print(df.columns.tolist())
['date', 'time', 'temperature', 'pressure', 'humidity', 'label', 'type']
>>> print(df.head())
        date      time  temperature  ...   humidity  label  type
0  25-Apr-19  17:33:16    40.881866  ...  38.363631      1  ddos
1  25-Apr-19  17:33:16    44.913806  ...  46.141423      1  ddos
2  25-Apr-19  17:33:16    38.295822  ...  50.850643      1  ddos
3  25-Apr-19  17:33:21    41.306586  ...  38.363631      1  ddos
4  25-Apr-19  17:33:21    44.903178  ...  46.141423      1  ddos

[5 rows x 7 columns]
>>> import pandas as pd
>>> df=pd.read_csv(r"D:\datasets\raw\ton_iot\train_test_network\.csv")
>>> print(df.shape)
(211043, 44)
>>> print(df.columns.tolist())
['src_ip', 'src_port', 'dst_ip', 'dst_port', 'proto', 'service', 'duration', 'src_bytes', 'dst_bytes', 'conn_state', 'missed_bytes', 'src_pkts', 'src_ip_bytes', 'dst_pkts', 'dst_ip_bytes', 'dns_query', 'dns_qclass', 'dns_qtype', 'dns_rcode', 'dns_AA', 'dns_RD', 'dns_RA', 'dns_rejected', 'ssl_version', 'ssl_cipher', 'ssl_resumed', 'ssl_established', 'ssl_subject', 'ssl_issuer', 'http_trans_depth', 'http_method', 'http_uri', 'http_version', 'http_request_body_len', 'http_response_body_len', 'http_status_code', 'http_user_agent', 'http_orig_mime_types', 'http_resp_mime_types', 'weird_name', 'weird_addl', 'weird_notice', 'label', 'type']
>>> print(df.head())
          src_ip  src_port  ... label      type
0   192.168.1.37      4444  ...     1  backdoor
1  192.168.1.193     49180  ...     1  backdoor
2  192.168.1.193     49180  ...     1  backdoor
3  192.168.1.193     49180  ...     1  backdoor
4  192.168.1.193     49180  ...     1  backdoor

[5 rows x 44 columns]

Quick Notes : 

All 4 files load cleanly — nice, that's Phase 2 fully wrapped up. Quick read on what you've got:

Modbus: 31,106 rows, function-code columns + label/type
Thermostat: 32,774 rows, temperature + status + label/type
Weather: 39,260 rows, temp/pressure/humidity + label/type
Network: 211,043 rows, 44 columns (real network flow features — IPs, ports, protocol, plus DNS/SSL/HTTP metadata) + label/type

One thing to know upfront about the Network file: a lot of those DNS/SSL/HTTP columns will show heavy nulls when you profile it — that's expected, not a data quality problem. A connection either has DNS or SSL or HTTP fields populated, not all three at once, so most rows will be null in two of those three groups. Don't try to "fix" that in cleaning — it's normal structure, not junk data.