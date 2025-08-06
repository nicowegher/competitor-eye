2025-08-06T12:13:59.72068136Z ==> Cloning from https://github.com/nicowegher/competitor-eye
2025-08-06T12:14:00.160976303Z ==> Checking out commit eff21eda572a59d240368c099dbc4c05d94d1edf in branch main
2025-08-06T12:14:01.212192473Z ==> Downloading cache...
2025-08-06T12:14:13.519581593Z ==> Transferred 198MB in 8s. Extraction took 3s.
2025-08-06T12:14:20.315474605Z ==> Installing Python version 3.11.8...
2025-08-06T12:14:28.055114138Z ==> Using Python version 3.11.8 via /opt/render/project/src/.python-version
2025-08-06T12:14:28.08151033Z ==> Docs on specifying a Python version: https://render.com/docs/python-version
2025-08-06T12:14:32.29238871Z ==> Using Poetry version 2.1.3 (default)
2025-08-06T12:14:32.342904575Z ==> Docs on specifying a Poetry version: https://render.com/docs/poetry-version
2025-08-06T12:14:32.362059375Z ==> Running build command 'pip install -r requirements.txt'...
2025-08-06T12:14:32.888877417Z Collecting Flask==2.3.3 (from -r requirements.txt (line 1))
2025-08-06T12:14:32.891066222Z   Using cached flask-2.3.3-py3-none-any.whl.metadata (3.6 kB)
2025-08-06T12:14:32.932485399Z Collecting flask-cors==4.0.0 (from -r requirements.txt (line 2))
2025-08-06T12:14:32.935493465Z   Using cached Flask_Cors-4.0.0-py2.py3-none-any.whl.metadata (5.4 kB)
2025-08-06T12:14:33.193652234Z Collecting numpy==1.24.4 (from -r requirements.txt (line 3))
2025-08-06T12:14:33.196414324Z   Using cached numpy-1.24.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (5.6 kB)
2025-08-06T12:14:33.344237768Z Collecting pandas==2.0.3 (from -r requirements.txt (line 4))
2025-08-06T12:14:33.346675089Z   Using cached pandas-2.0.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (18 kB)
2025-08-06T12:14:33.396831306Z Collecting openpyxl==3.1.2 (from -r requirements.txt (line 5))
2025-08-06T12:14:33.39898479Z   Using cached openpyxl-3.1.2-py2.py3-none-any.whl.metadata (2.5 kB)
2025-08-06T12:14:33.45446711Z Collecting requests==2.31.0 (from -r requirements.txt (line 6))
2025-08-06T12:14:33.456780538Z   Using cached requests-2.31.0-py3-none-any.whl.metadata (4.6 kB)
2025-08-06T12:14:33.493542629Z Collecting python-dotenv==1.0.0 (from -r requirements.txt (line 7))
2025-08-06T12:14:33.495816526Z   Using cached python_dotenv-1.0.0-py3-none-any.whl.metadata (21 kB)
2025-08-06T12:14:33.542785973Z Collecting firebase-admin==6.4.0 (from -r requirements.txt (line 8))
2025-08-06T12:14:33.545005719Z   Using cached firebase_admin-6.4.0-py3-none-any.whl.metadata (1.5 kB)
2025-08-06T12:14:33.603232488Z Collecting google-cloud-storage==2.16.0 (from -r requirements.txt (line 9))
2025-08-06T12:14:33.605046703Z   Using cached google_cloud_storage-2.16.0-py2.py3-none-any.whl.metadata (6.1 kB)
2025-08-06T12:14:33.751878263Z Collecting apify-client (from -r requirements.txt (line 10))
2025-08-06T12:14:33.808400439Z   Downloading apify_client-1.12.1-py3-none-any.whl.metadata (17 kB)
2025-08-06T12:14:33.854460643Z Collecting gunicorn (from -r requirements.txt (line 11))
2025-08-06T12:14:33.856562936Z   Using cached gunicorn-23.0.0-py3-none-any.whl.metadata (4.4 kB)
2025-08-06T12:14:33.89222031Z Collecting mailersend (from -r requirements.txt (line 12))
2025-08-06T12:14:33.905071442Z   Downloading mailersend-2.0.0-py3-none-any.whl.metadata (572 bytes)
2025-08-06T12:14:34.009631252Z Collecting mercadopago==2.3.0 (from -r requirements.txt (line 13))
2025-08-06T12:14:34.011514259Z   Using cached mercadopago-2.3.0-py3-none-any.whl.metadata (5.6 kB)
2025-08-06T12:14:34.058999979Z Collecting Werkzeug>=2.3.7 (from Flask==2.3.3->-r requirements.txt (line 1))
2025-08-06T12:14:34.060847875Z   Using cached werkzeug-3.1.3-py3-none-any.whl.metadata (3.7 kB)
2025-08-06T12:14:34.091034932Z Collecting Jinja2>=3.1.2 (from Flask==2.3.3->-r requirements.txt (line 1))
2025-08-06T12:14:34.092752335Z   Using cached jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
2025-08-06T12:14:34.118056819Z Collecting itsdangerous>=2.1.2 (from Flask==2.3.3->-r requirements.txt (line 1))
2025-08-06T12:14:34.119755282Z   Using cached itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
2025-08-06T12:14:34.157757494Z Collecting click>=8.1.3 (from Flask==2.3.3->-r requirements.txt (line 1))
2025-08-06T12:14:34.159502258Z   Using cached click-8.2.1-py3-none-any.whl.metadata (2.5 kB)
2025-08-06T12:14:34.183423477Z Collecting blinker>=1.6.2 (from Flask==2.3.3->-r requirements.txt (line 1))
2025-08-06T12:14:34.185183641Z   Using cached blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
2025-08-06T12:14:34.268295704Z Collecting python-dateutil>=2.8.2 (from pandas==2.0.3->-r requirements.txt (line 4))
2025-08-06T12:14:34.270468248Z   Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl.metadata (8.4 kB)
2025-08-06T12:14:34.328872002Z Collecting pytz>=2020.1 (from pandas==2.0.3->-r requirements.txt (line 4))
2025-08-06T12:14:34.330892282Z   Using cached pytz-2025.2-py2.py3-none-any.whl.metadata (22 kB)
2025-08-06T12:14:34.362139325Z Collecting tzdata>=2022.1 (from pandas==2.0.3->-r requirements.txt (line 4))
2025-08-06T12:14:34.364043753Z   Using cached tzdata-2025.2-py2.py3-none-any.whl.metadata (1.4 kB)
2025-08-06T12:14:34.398317392Z Collecting et-xmlfile (from openpyxl==3.1.2->-r requirements.txt (line 5))
2025-08-06T12:14:34.400146018Z   Using cached et_xmlfile-2.0.0-py3-none-any.whl.metadata (2.7 kB)
2025-08-06T12:14:34.500093393Z Collecting charset-normalizer<4,>=2 (from requests==2.31.0->-r requirements.txt (line 6))
2025-08-06T12:14:34.502144154Z   Using cached charset_normalizer-3.4.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (35 kB)
2025-08-06T12:14:34.534747961Z Collecting idna<4,>=2.5 (from requests==2.31.0->-r requirements.txt (line 6))
2025-08-06T12:14:34.536550576Z   Using cached idna-3.10-py3-none-any.whl.metadata (10 kB)
2025-08-06T12:14:34.590240941Z Collecting urllib3<3,>=1.21.1 (from requests==2.31.0->-r requirements.txt (line 6))
2025-08-06T12:14:34.592214461Z   Using cached urllib3-2.5.0-py3-none-any.whl.metadata (6.5 kB)
2025-08-06T12:14:34.635003313Z Collecting certifi>=2017.4.17 (from requests==2.31.0->-r requirements.txt (line 6))
2025-08-06T12:14:34.644181673Z   Downloading certifi-2025.8.3-py3-none-any.whl.metadata (2.4 kB)
2025-08-06T12:14:34.694362271Z Collecting cachecontrol>=0.12.6 (from firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:34.696213567Z   Using cached cachecontrol-0.14.3-py3-none-any.whl.metadata (3.1 kB)
2025-08-06T12:14:34.834883012Z Collecting google-api-python-client>=1.7.8 (from firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:34.844037241Z   Downloading google_api_python_client-2.177.0-py3-none-any.whl.metadata (7.0 kB)
2025-08-06T12:14:34.896766993Z Collecting pyjwt>=2.5.0 (from pyjwt[crypto]>=2.5.0->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:34.898551867Z   Using cached PyJWT-2.10.1-py3-none-any.whl.metadata (4.0 kB)
2025-08-06T12:14:34.975779813Z Collecting google-api-core<3.0.0dev,>=1.22.1 (from google-api-core[grpc]<3.0.0dev,>=1.22.1; platform_python_implementation != "PyPy"->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:34.977575828Z   Using cached google_api_core-2.25.1-py3-none-any.whl.metadata (3.0 kB)
2025-08-06T12:14:35.024949125Z Collecting google-cloud-firestore>=2.9.1 (from firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:35.02673409Z   Using cached google_cloud_firestore-2.21.0-py3-none-any.whl.metadata (9.9 kB)
2025-08-06T12:14:35.122248233Z Collecting google-auth<3.0dev,>=2.26.1 (from google-cloud-storage==2.16.0->-r requirements.txt (line 9))
2025-08-06T12:14:35.124232583Z   Using cached google_auth-2.40.3-py2.py3-none-any.whl.metadata (6.2 kB)
2025-08-06T12:14:35.174887412Z Collecting google-cloud-core<3.0dev,>=2.3.0 (from google-cloud-storage==2.16.0->-r requirements.txt (line 9))
2025-08-06T12:14:35.176729878Z   Using cached google_cloud_core-2.4.3-py2.py3-none-any.whl.metadata (2.7 kB)
2025-08-06T12:14:35.215928391Z Collecting google-resumable-media>=2.6.0 (from google-cloud-storage==2.16.0->-r requirements.txt (line 9))
2025-08-06T12:14:35.217735286Z   Using cached google_resumable_media-2.7.2-py2.py3-none-any.whl.metadata (2.2 kB)
2025-08-06T12:14:35.310004378Z Collecting google-crc32c<2.0dev,>=1.0 (from google-cloud-storage==2.16.0->-r requirements.txt (line 9))
2025-08-06T12:14:35.311884335Z   Using cached google_crc32c-1.7.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (2.3 kB)
2025-08-06T12:14:35.363574301Z Collecting apify-shared<2.0.0 (from apify-client->-r requirements.txt (line 10))
2025-08-06T12:14:35.373184111Z   Downloading apify_shared-1.5.0-py3-none-any.whl.metadata (2.5 kB)
2025-08-06T12:14:35.415257396Z Collecting colorama>=0.4.0 (from apify-client->-r requirements.txt (line 10))
2025-08-06T12:14:35.416961358Z   Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
2025-08-06T12:14:35.463092165Z Collecting httpx>=0.25 (from apify-client->-r requirements.txt (line 10))
2025-08-06T12:14:35.465014162Z   Using cached httpx-0.28.1-py3-none-any.whl.metadata (7.1 kB)
2025-08-06T12:14:35.499053826Z Collecting more-itertools>=10.0.0 (from apify-client->-r requirements.txt (line 10))
2025-08-06T12:14:35.500973604Z   Using cached more_itertools-10.7.0-py3-none-any.whl.metadata (37 kB)
2025-08-06T12:14:35.544378001Z Collecting packaging (from gunicorn->-r requirements.txt (line 11))
2025-08-06T12:14:35.546230088Z   Using cached packaging-25.0-py3-none-any.whl.metadata (3.3 kB)
2025-08-06T12:14:35.718901155Z Collecting pydantic<3.0.0,>=2.11.0 (from pydantic[email]<3.0.0,>=2.11.0->mailersend->-r requirements.txt (line 12))
2025-08-06T12:14:35.728397053Z   Downloading pydantic-2.11.7-py3-none-any.whl.metadata (67 kB)
2025-08-06T12:14:35.749388899Z      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 68.0/68.0 kB 3.2 MB/s eta 0:00:00
2025-08-06T12:14:35.926417645Z Collecting msgpack<2.0.0,>=0.5.2 (from cachecontrol>=0.12.6->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:35.928481047Z   Using cached msgpack-1.1.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (8.4 kB)
2025-08-06T12:14:35.998015569Z Collecting googleapis-common-protos<2.0.0,>=1.56.2 (from google-api-core<3.0.0dev,>=1.22.1->google-api-core[grpc]<3.0.0dev,>=1.22.1; platform_python_implementation != "PyPy"->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:35.999816244Z   Using cached googleapis_common_protos-1.70.0-py3-none-any.whl.metadata (9.3 kB)
2025-08-06T12:14:36.257854421Z Collecting protobuf!=3.20.0,!=3.20.1,!=4.21.0,!=4.21.1,!=4.21.2,!=4.21.3,!=4.21.4,!=4.21.5,<7.0.0,>=3.19.5 (from google-api-core<3.0.0dev,>=1.22.1->google-api-core[grpc]<3.0.0dev,>=1.22.1; platform_python_implementation != "PyPy"->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:36.259887151Z   Using cached protobuf-6.31.1-cp39-abi3-manylinux2014_x86_64.whl.metadata (593 bytes)
2025-08-06T12:14:36.297246318Z Collecting proto-plus<2.0.0,>=1.22.3 (from google-api-core<3.0.0dev,>=1.22.1->google-api-core[grpc]<3.0.0dev,>=1.22.1; platform_python_implementation != "PyPy"->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:36.299053023Z   Using cached proto_plus-1.26.1-py3-none-any.whl.metadata (2.2 kB)
2025-08-06T12:14:36.971756031Z Collecting grpcio<2.0.0,>=1.33.2 (from google-api-core[grpc]<3.0.0dev,>=1.22.1; platform_python_implementation != "PyPy"->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:36.981542526Z   Downloading grpcio-1.74.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.8 kB)
2025-08-06T12:14:37.074541986Z Collecting grpcio-status<2.0.0,>=1.33.2 (from google-api-core[grpc]<3.0.0dev,>=1.22.1; platform_python_implementation != "PyPy"->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:37.08389038Z   Downloading grpcio_status-1.74.0-py3-none-any.whl.metadata (1.1 kB)
2025-08-06T12:14:37.14452255Z Collecting httplib2<1.0.0,>=0.19.0 (from google-api-python-client>=1.7.8->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:37.146584412Z   Using cached httplib2-0.22.0-py3-none-any.whl.metadata (2.6 kB)
2025-08-06T12:14:37.190458121Z Collecting google-auth-httplib2<1.0.0,>=0.2.0 (from google-api-python-client>=1.7.8->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:37.192326408Z   Using cached google_auth_httplib2-0.2.0-py2.py3-none-any.whl.metadata (2.2 kB)
2025-08-06T12:14:37.218822252Z Collecting uritemplate<5,>=3.0.1 (from google-api-python-client>=1.7.8->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:37.220815462Z   Using cached uritemplate-4.2.0-py3-none-any.whl.metadata (2.6 kB)
2025-08-06T12:14:37.364197425Z Collecting cachetools<6.0,>=2.0.0 (from google-auth<3.0dev,>=2.26.1->google-cloud-storage==2.16.0->-r requirements.txt (line 9))
2025-08-06T12:14:37.366285287Z   Using cached cachetools-5.5.2-py3-none-any.whl.metadata (5.4 kB)
2025-08-06T12:14:37.401817517Z Collecting pyasn1-modules>=0.2.1 (from google-auth<3.0dev,>=2.26.1->google-cloud-storage==2.16.0->-r requirements.txt (line 9))
2025-08-06T12:14:37.403806267Z   Using cached pyasn1_modules-0.4.2-py3-none-any.whl.metadata (3.5 kB)
2025-08-06T12:14:37.434496456Z Collecting rsa<5,>=3.1.4 (from google-auth<3.0dev,>=2.26.1->google-cloud-storage==2.16.0->-r requirements.txt (line 9))
2025-08-06T12:14:37.436382103Z   Using cached rsa-4.9.1-py3-none-any.whl.metadata (5.6 kB)
2025-08-06T12:14:37.620672242Z Collecting anyio (from httpx>=0.25->apify-client->-r requirements.txt (line 10))
2025-08-06T12:14:37.629900993Z   Downloading anyio-4.10.0-py3-none-any.whl.metadata (4.0 kB)
2025-08-06T12:14:37.678296596Z Collecting httpcore==1.* (from httpx>=0.25->apify-client->-r requirements.txt (line 10))
2025-08-06T12:14:37.680297546Z   Using cached httpcore-1.0.9-py3-none-any.whl.metadata (21 kB)
2025-08-06T12:14:37.717008056Z Collecting h11>=0.16 (from httpcore==1.*->httpx>=0.25->apify-client->-r requirements.txt (line 10))
2025-08-06T12:14:37.7191462Z   Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
2025-08-06T12:14:37.810438577Z Collecting MarkupSafe>=2.0 (from Jinja2>=3.1.2->Flask==2.3.3->-r requirements.txt (line 1))
2025-08-06T12:14:37.812570621Z   Using cached MarkupSafe-3.0.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.0 kB)
2025-08-06T12:14:37.87120656Z Collecting annotated-types>=0.6.0 (from pydantic<3.0.0,>=2.11.0->pydantic[email]<3.0.0,>=2.11.0->mailersend->-r requirements.txt (line 12))
2025-08-06T12:14:37.880982845Z   Downloading annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
2025-08-06T12:14:38.782438895Z Collecting pydantic-core==2.33.2 (from pydantic<3.0.0,>=2.11.0->pydantic[email]<3.0.0,>=2.11.0->mailersend->-r requirements.txt (line 12))
2025-08-06T12:14:38.794767104Z   Downloading pydantic_core-2.33.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.8 kB)
2025-08-06T12:14:38.844634844Z Collecting typing-extensions>=4.12.2 (from pydantic<3.0.0,>=2.11.0->pydantic[email]<3.0.0,>=2.11.0->mailersend->-r requirements.txt (line 12))
2025-08-06T12:14:38.847187017Z   Using cached typing_extensions-4.14.1-py3-none-any.whl.metadata (3.0 kB)
2025-08-06T12:14:38.878593924Z Collecting typing-inspection>=0.4.0 (from pydantic<3.0.0,>=2.11.0->pydantic[email]<3.0.0,>=2.11.0->mailersend->-r requirements.txt (line 12))
2025-08-06T12:14:38.88801738Z   Downloading typing_inspection-0.4.1-py3-none-any.whl.metadata (2.6 kB)
2025-08-06T12:14:38.96061291Z Collecting email-validator>=2.0.0 (from pydantic[email]<3.0.0,>=2.11.0->mailersend->-r requirements.txt (line 12))
2025-08-06T12:14:38.96941528Z   Downloading email_validator-2.2.0-py3-none-any.whl.metadata (25 kB)
2025-08-06T12:14:39.23238655Z Collecting cryptography>=3.4.0 (from pyjwt[crypto]>=2.5.0->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:39.241605341Z   Downloading cryptography-45.0.6-cp311-abi3-manylinux_2_34_x86_64.whl.metadata (5.7 kB)
2025-08-06T12:14:39.289566713Z Collecting six>=1.5 (from python-dateutil>=2.8.2->pandas==2.0.3->-r requirements.txt (line 4))
2025-08-06T12:14:39.291388499Z   Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
2025-08-06T12:14:39.502165281Z Collecting cffi>=1.14 (from cryptography>=3.4.0->pyjwt[crypto]>=2.5.0->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:39.50414093Z   Using cached cffi-1.17.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (1.5 kB)
2025-08-06T12:14:39.549114937Z Collecting dnspython>=2.0.0 (from email-validator>=2.0.0->pydantic[email]<3.0.0,>=2.11.0->mailersend->-r requirements.txt (line 12))
2025-08-06T12:14:39.558479992Z   Downloading dnspython-2.7.0-py3-none-any.whl.metadata (5.8 kB)
2025-08-06T12:14:39.740870512Z Collecting pyparsing!=3.0.0,!=3.0.1,!=3.0.2,!=3.0.3,<4,>=2.4.2 (from httplib2<1.0.0,>=0.19.0->google-api-python-client>=1.7.8->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:39.742828812Z   Using cached pyparsing-3.2.3-py3-none-any.whl.metadata (5.0 kB)
2025-08-06T12:14:39.889319063Z Collecting pyasn1<0.7.0,>=0.6.1 (from pyasn1-modules>=0.2.1->google-auth<3.0dev,>=2.26.1->google-cloud-storage==2.16.0->-r requirements.txt (line 9))
2025-08-06T12:14:39.891291462Z   Using cached pyasn1-0.6.1-py3-none-any.whl.metadata (8.4 kB)
2025-08-06T12:14:40.001159515Z Collecting sniffio>=1.1 (from anyio->httpx>=0.25->apify-client->-r requirements.txt (line 10))
2025-08-06T12:14:40.003031762Z   Using cached sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
2025-08-06T12:14:40.042195434Z Collecting pycparser (from cffi>=1.14->cryptography>=3.4.0->pyjwt[crypto]>=2.5.0->firebase-admin==6.4.0->-r requirements.txt (line 8))
2025-08-06T12:14:40.043915187Z   Using cached pycparser-2.22-py3-none-any.whl.metadata (943 bytes)
2025-08-06T12:14:40.139747608Z Using cached flask-2.3.3-py3-none-any.whl (96 kB)
2025-08-06T12:14:40.141489252Z Using cached Flask_Cors-4.0.0-py2.py3-none-any.whl (14 kB)
2025-08-06T12:14:40.143082682Z Using cached numpy-1.24.4-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (17.3 MB)
2025-08-06T12:14:40.172347965Z Using cached pandas-2.0.3-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (12.2 MB)
2025-08-06T12:14:40.193717571Z Using cached openpyxl-3.1.2-py2.py3-none-any.whl (249 kB)
2025-08-06T12:14:40.19570455Z Using cached requests-2.31.0-py3-none-any.whl (62 kB)
2025-08-06T12:14:40.197373662Z Using cached python_dotenv-1.0.0-py3-none-any.whl (19 kB)
2025-08-06T12:14:40.198976863Z Using cached firebase_admin-6.4.0-py3-none-any.whl (120 kB)
2025-08-06T12:14:40.200677345Z Using cached google_cloud_storage-2.16.0-py2.py3-none-any.whl (125 kB)
2025-08-06T12:14:40.202426439Z Using cached mercadopago-2.3.0-py3-none-any.whl (35 kB)
2025-08-06T12:14:40.211961558Z Downloading apify_client-1.12.1-py3-none-any.whl (83 kB)
2025-08-06T12:14:40.227446386Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 83.2/83.2 kB 5.5 MB/s eta 0:00:00
2025-08-06T12:14:40.229104667Z Using cached gunicorn-23.0.0-py3-none-any.whl (85 kB)
2025-08-06T12:14:40.239211101Z Downloading mailersend-2.0.0-py3-none-any.whl (101 kB)
2025-08-06T12:14:40.253520639Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 101.9/101.9 kB 7.5 MB/s eta 0:00:00
2025-08-06T12:14:40.263081429Z Downloading apify_shared-1.5.0-py3-none-any.whl (13 kB)
2025-08-06T12:14:40.27430741Z Using cached blinker-1.9.0-py3-none-any.whl (8.5 kB)
2025-08-06T12:14:40.27589871Z Using cached cachecontrol-0.14.3-py3-none-any.whl (21 kB)
2025-08-06T12:14:40.284804063Z Downloading certifi-2025.8.3-py3-none-any.whl (161 kB)
2025-08-06T12:14:40.299716417Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 161.2/161.2 kB 11.9 MB/s eta 0:00:00
2025-08-06T12:14:40.301467231Z Using cached charset_normalizer-3.4.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (147 kB)
2025-08-06T12:14:40.303323178Z Using cached click-8.2.1-py3-none-any.whl (102 kB)
2025-08-06T12:14:40.305156173Z Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
2025-08-06T12:14:40.306794034Z Using cached google_api_core-2.25.1-py3-none-any.whl (160 kB)
2025-08-06T12:14:40.316134568Z Downloading google_api_python_client-2.177.0-py3-none-any.whl (13.7 MB)
2025-08-06T12:14:40.438272089Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 13.7/13.7 MB 111.2 MB/s eta 0:00:00
2025-08-06T12:14:40.440161727Z Using cached google_auth-2.40.3-py2.py3-none-any.whl (216 kB)
2025-08-06T12:14:40.442187687Z Using cached google_cloud_core-2.4.3-py2.py3-none-any.whl (29 kB)
2025-08-06T12:14:40.443802328Z Using cached google_cloud_firestore-2.21.0-py3-none-any.whl (368 kB)
2025-08-06T12:14:40.445975612Z Using cached google_crc32c-1.7.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (32 kB)
2025-08-06T12:14:40.447607593Z Using cached google_resumable_media-2.7.2-py2.py3-none-any.whl (81 kB)
2025-08-06T12:14:40.449319426Z Using cached httpx-0.28.1-py3-none-any.whl (73 kB)
2025-08-06T12:14:40.451016668Z Using cached httpcore-1.0.9-py3-none-any.whl (78 kB)
2025-08-06T12:14:40.45268083Z Using cached idna-3.10-py3-none-any.whl (70 kB)
2025-08-06T12:14:40.454414704Z Using cached itsdangerous-2.2.0-py3-none-any.whl (16 kB)
2025-08-06T12:14:40.456033624Z Using cached jinja2-3.1.6-py3-none-any.whl (134 kB)
2025-08-06T12:14:40.457832529Z Using cached more_itertools-10.7.0-py3-none-any.whl (65 kB)
2025-08-06T12:14:40.467013699Z Downloading pydantic-2.11.7-py3-none-any.whl (444 kB)
2025-08-06T12:14:40.48381537Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 444.8/444.8 kB 29.7 MB/s eta 0:00:00
2025-08-06T12:14:40.492923109Z Downloading pydantic_core-2.33.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.0 MB)
2025-08-06T12:14:40.523624848Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.0/2.0 MB 69.6 MB/s eta 0:00:00
2025-08-06T12:14:40.525320041Z Using cached PyJWT-2.10.1-py3-none-any.whl (22 kB)
2025-08-06T12:14:40.526918171Z Using cached python_dateutil-2.9.0.post0-py2.py3-none-any.whl (229 kB)
2025-08-06T12:14:40.528822978Z Using cached pytz-2025.2-py2.py3-none-any.whl (509 kB)
2025-08-06T12:14:40.531153467Z Using cached tzdata-2025.2-py2.py3-none-any.whl (347 kB)
2025-08-06T12:14:40.533224539Z Using cached urllib3-2.5.0-py3-none-any.whl (129 kB)
2025-08-06T12:14:40.534952222Z Using cached werkzeug-3.1.3-py3-none-any.whl (224 kB)
2025-08-06T12:14:40.53685247Z Using cached et_xmlfile-2.0.0-py3-none-any.whl (18 kB)
2025-08-06T12:14:40.538416419Z Using cached packaging-25.0-py3-none-any.whl (66 kB)
2025-08-06T12:14:40.547441005Z Downloading annotated_types-0.7.0-py3-none-any.whl (13 kB)
2025-08-06T12:14:40.560378889Z Using cached cachetools-5.5.2-py3-none-any.whl (10 kB)
2025-08-06T12:14:40.569435986Z Downloading cryptography-45.0.6-cp311-abi3-manylinux_2_34_x86_64.whl (4.5 MB)
2025-08-06T12:14:40.615340186Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.5/4.5 MB 101.8 MB/s eta 0:00:00
2025-08-06T12:14:40.624381973Z Downloading email_validator-2.2.0-py3-none-any.whl (33 kB)
2025-08-06T12:14:40.633538202Z Using cached google_auth_httplib2-0.2.0-py2.py3-none-any.whl (9.3 kB)
2025-08-06T12:14:40.635107722Z Using cached googleapis_common_protos-1.70.0-py3-none-any.whl (294 kB)
2025-08-06T12:14:40.644558349Z Downloading grpcio-1.74.0-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (6.2 MB)
2025-08-06T12:14:40.698276515Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 6.2/6.2 MB 120.3 MB/s eta 0:00:00
2025-08-06T12:14:40.70766939Z Downloading grpcio_status-1.74.0-py3-none-any.whl (14 kB)
2025-08-06T12:14:40.719584489Z Using cached httplib2-0.22.0-py3-none-any.whl (96 kB)
2025-08-06T12:14:40.721341333Z Using cached MarkupSafe-3.0.2-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (23 kB)
2025-08-06T12:14:40.722942293Z Using cached msgpack-1.1.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (429 kB)
2025-08-06T12:14:40.725169649Z Using cached proto_plus-1.26.1-py3-none-any.whl (50 kB)
2025-08-06T12:14:40.7268007Z Using cached protobuf-6.31.1-cp39-abi3-manylinux2014_x86_64.whl (321 kB)
2025-08-06T12:14:40.728861371Z Using cached pyasn1_modules-0.4.2-py3-none-any.whl (181 kB)
2025-08-06T12:14:40.730674217Z Using cached rsa-4.9.1-py3-none-any.whl (34 kB)
2025-08-06T12:14:40.732293417Z Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
2025-08-06T12:14:40.733864087Z Using cached typing_extensions-4.14.1-py3-none-any.whl (43 kB)
2025-08-06T12:14:40.742916274Z Downloading typing_inspection-0.4.1-py3-none-any.whl (14 kB)
2025-08-06T12:14:40.756452682Z Using cached uritemplate-4.2.0-py3-none-any.whl (11 kB)
2025-08-06T12:14:40.765572081Z Downloading anyio-4.10.0-py3-none-any.whl (107 kB)
2025-08-06T12:14:40.779190163Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 107.2/107.2 kB 8.3 MB/s eta 0:00:00
2025-08-06T12:14:40.780838204Z Using cached cffi-1.17.1-cp311-cp311-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (467 kB)
2025-08-06T12:14:40.790400513Z Downloading dnspython-2.7.0-py3-none-any.whl (313 kB)
2025-08-06T12:14:40.805924912Z    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 313.6/313.6 kB 22.3 MB/s eta 0:00:00
2025-08-06T12:14:40.807497642Z Using cached h11-0.16.0-py3-none-any.whl (37 kB)
2025-08-06T12:14:40.809140093Z Using cached pyasn1-0.6.1-py3-none-any.whl (83 kB)
2025-08-06T12:14:40.810857746Z Using cached pyparsing-3.2.3-py3-none-any.whl (111 kB)
2025-08-06T12:14:40.812560119Z Using cached sniffio-1.3.1-py3-none-any.whl (10 kB)
2025-08-06T12:14:40.814133528Z Using cached pycparser-2.22-py3-none-any.whl (117 kB)
2025-08-06T12:14:41.349231047Z Installing collected packages: pytz, urllib3, uritemplate, tzdata, typing-extensions, sniffio, six, python-dotenv, pyparsing, pyjwt, pycparser, pyasn1, protobuf, packaging, numpy, msgpack, more-itertools, MarkupSafe, itsdangerous, idna, h11, grpcio, google-crc32c, et-xmlfile, dnspython, colorama, click, charset-normalizer, certifi, cachetools, blinker, apify-shared, annotated-types, Werkzeug, typing-inspection, rsa, requests, python-dateutil, pydantic-core, pyasn1-modules, proto-plus, openpyxl, Jinja2, httplib2, httpcore, gunicorn, googleapis-common-protos, google-resumable-media, email-validator, cffi, anyio, pydantic, pandas, mercadopago, httpx, grpcio-status, google-auth, Flask, cryptography, cachecontrol, google-auth-httplib2, google-api-core, flask-cors, apify-client, mailersend, google-cloud-core, google-api-python-client, google-cloud-storage, google-cloud-firestore, firebase-admin
2025-08-06T12:14:52.944424392Z Successfully installed Flask-2.3.3 Jinja2-3.1.6 MarkupSafe-3.0.2 Werkzeug-3.1.3 annotated-types-0.7.0 anyio-4.10.0 apify-client-1.12.1 apify-shared-1.5.0 blinker-1.9.0 cachecontrol-0.14.3 cachetools-5.5.2 certifi-2025.8.3 cffi-1.17.1 charset-normalizer-3.4.2 click-8.2.1 colorama-0.4.6 cryptography-45.0.6 dnspython-2.7.0 email-validator-2.2.0 et-xmlfile-2.0.0 firebase-admin-6.4.0 flask-cors-4.0.0 google-api-core-2.25.1 google-api-python-client-2.177.0 google-auth-2.40.3 google-auth-httplib2-0.2.0 google-cloud-core-2.4.3 google-cloud-firestore-2.21.0 google-cloud-storage-2.16.0 google-crc32c-1.7.1 google-resumable-media-2.7.2 googleapis-common-protos-1.70.0 grpcio-1.74.0 grpcio-status-1.74.0 gunicorn-23.0.0 h11-0.16.0 httpcore-1.0.9 httplib2-0.22.0 httpx-0.28.1 idna-3.10 itsdangerous-2.2.0 mailersend-2.0.0 mercadopago-2.3.0 more-itertools-10.7.0 msgpack-1.1.1 numpy-1.24.4 openpyxl-3.1.2 packaging-25.0 pandas-2.0.3 proto-plus-1.26.1 protobuf-6.31.1 pyasn1-0.6.1 pyasn1-modules-0.4.2 pycparser-2.22 pydantic-2.11.7 pydantic-core-2.33.2 pyjwt-2.10.1 pyparsing-3.2.3 python-dateutil-2.9.0.post0 python-dotenv-1.0.0 pytz-2025.2 requests-2.31.0 rsa-4.9.1 six-1.17.0 sniffio-1.3.1 typing-extensions-4.14.1 typing-inspection-0.4.1 tzdata-2025.2 uritemplate-4.2.0 urllib3-2.5.0
2025-08-06T12:14:53.141608444Z 
2025-08-06T12:14:53.141634784Z [notice] A new release of pip is available: 24.0 -> 25.2
2025-08-06T12:14:53.141640074Z [notice] To update, run: pip install --upgrade pip
2025-08-06T12:15:00.881977832Z ==> Uploading build...
2025-08-06T12:15:20.320093699Z ==> Uploaded in 15.7s. Compression took 3.7s
2025-08-06T12:15:20.412220848Z ==> Build successful 🎉
2025-08-06T12:15:23.294548341Z ==> Deploying...
2025-08-06T12:16:11.518763275Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/base.py", line 235, in run
2025-08-06T12:16:11.518902069Z     super().run()
2025-08-06T12:16:11.51896435Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/base.py", line 71, in run
2025-08-06T12:16:11.519094193Z     Arbiter(self).run()
2025-08-06T12:16:11.519099223Z     ^^^^^^^^^^^^^
2025-08-06T12:16:11.519101973Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/arbiter.py", line 57, in __init__
2025-08-06T12:16:11.519212106Z     self.setup(app)
2025-08-06T12:16:11.519221746Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/arbiter.py", line 117, in setup
2025-08-06T12:16:11.519322349Z     self.app.wsgi()
2025-08-06T12:16:11.519326669Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/base.py", line 66, in wsgi
2025-08-06T12:16:11.519426601Z     self.callable = self.load()
2025-08-06T12:16:11.519436341Z                     ^^^^^^^^^^^
2025-08-06T12:16:11.519439262Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
2025-08-06T12:16:11.519546224Z     return self.load_wsgiapp()
2025-08-06T12:16:11.519586795Z            ^^^^^^^^^^^^^^^^^^^
2025-08-06T12:16:11.519592845Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
2025-08-06T12:16:11.519687437Z     return util.import_app(self.app_uri)
2025-08-06T12:16:11.519697608Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-06T12:16:11.519700738Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/util.py", line 370, in import_app
2025-08-06T12:16:11.519903533Z     mod = importlib.import_module(module)
2025-08-06T12:16:11.519918643Z           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-06T12:16:11.519923583Z   File "/opt/render/project/python/Python-3.11.8/lib/python3.11/importlib/__init__.py", line 126, in import_module
2025-08-06T12:16:11.520053766Z     return _bootstrap._gcd_import(name[level:], package, level)
2025-08-06T12:16:11.520062966Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-06T12:16:11.520065686Z   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
2025-08-06T12:16:11.520071417Z   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
2025-08-06T12:16:11.520074397Z   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
2025-08-06T12:16:11.520080007Z   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
2025-08-06T12:16:11.520082747Z   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
2025-08-06T12:16:11.520088967Z   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
2025-08-06T12:16:11.520092167Z   File "/opt/render/project/src/app.py", line 17, in <module>
2025-08-06T12:16:11.52020407Z     from mailersend import emails
2025-08-06T12:16:11.52020934Z ImportError: cannot import name 'emails' from 'mailersend' (/opt/render/project/src/.venv/lib/python3.11/site-packages/mailersend/__init__.py)
2025-08-06T12:16:14.655644243Z ==> Exited with status 1
2025-08-06T12:16:14.67443929Z ==> Common ways to troubleshoot your deploy: https://render.com/docs/troubleshooting-deploys
2025-08-06T12:16:16.272500279Z ==> Running 'gunicorn app:app'
2025-08-06T12:16:19.59695713Z Traceback (most recent call last):
2025-08-06T12:16:19.596978891Z   File "/opt/render/project/src/.venv/bin/gunicorn", line 8, in <module>
2025-08-06T12:16:19.597019752Z     sys.exit(run())
2025-08-06T12:16:19.597035432Z              ^^^^^
2025-08-06T12:16:19.597042512Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 66, in run
2025-08-06T12:16:19.597157695Z     WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]", prog=prog).run()
2025-08-06T12:16:19.597168435Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/base.py", line 235, in run
2025-08-06T12:16:19.597331939Z     super().run()
2025-08-06T12:16:19.597348949Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/base.py", line 71, in run
2025-08-06T12:16:19.597434562Z     Arbiter(self).run()
2025-08-06T12:16:19.597440702Z     ^^^^^^^^^^^^^
2025-08-06T12:16:19.597444592Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/arbiter.py", line 57, in __init__
2025-08-06T12:16:19.597529614Z     self.setup(app)
2025-08-06T12:16:19.597549384Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/arbiter.py", line 117, in setup
2025-08-06T12:16:19.597635876Z     self.app.wsgi()
2025-08-06T12:16:19.597654537Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/base.py", line 66, in wsgi
2025-08-06T12:16:19.597747339Z     self.callable = self.load()
2025-08-06T12:16:19.597760899Z                     ^^^^^^^^^^^
2025-08-06T12:16:19.597763939Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 57, in load
2025-08-06T12:16:19.597884702Z     return self.load_wsgiapp()
2025-08-06T12:16:19.597896763Z            ^^^^^^^^^^^^^^^^^^^
2025-08-06T12:16:19.597900213Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp
2025-08-06T12:16:19.597999005Z     return util.import_app(self.app_uri)
2025-08-06T12:16:19.598035216Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-06T12:16:19.598040636Z   File "/opt/render/project/src/.venv/lib/python3.11/site-packages/gunicorn/util.py", line 370, in import_app
2025-08-06T12:16:19.59819152Z     mod = importlib.import_module(module)
2025-08-06T12:16:19.598243081Z           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-06T12:16:19.598247821Z   File "/opt/render/project/python/Python-3.11.8/lib/python3.11/importlib/__init__.py", line 126, in import_module
2025-08-06T12:16:19.598348544Z     return _bootstrap._gcd_import(name[level:], package, level)
2025-08-06T12:16:19.598406015Z            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
2025-08-06T12:16:19.598411245Z   File "<frozen importlib._bootstrap>", line 1204, in _gcd_import
2025-08-06T12:16:19.598414255Z   File "<frozen importlib._bootstrap>", line 1176, in _find_and_load
2025-08-06T12:16:19.598416935Z   File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked
2025-08-06T12:16:19.598419395Z   File "<frozen importlib._bootstrap>", line 690, in _load_unlocked
2025-08-06T12:16:19.598422015Z   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
2025-08-06T12:16:19.598424825Z   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
2025-08-06T12:16:19.598427885Z   File "/opt/render/project/src/app.py", line 17, in <module>
2025-08-06T12:16:19.598485637Z     from mailersend import emails
2025-08-06T12:16:19.598491587Z ImportError: cannot import name 'emails' from 'mailersend' (/opt/render/project/src/.venv/lib/python3.11/site-packages/mailersend/__init__.py)