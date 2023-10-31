# Nogizaka Member's Calendar Synchronization with Google Calendar

## Prerequisites
- Python 3.9 or higher
- Google Chrome driver 
- Google Account with attached Google Calendar ID
- (Optional) Google Service Account with attached Google Calendar ID

## Installation
1. Adjust the minor version of `chromedriver_binary` in `requirements.txt`.
2. Install the Python packages listed in `requirements.txt`.
```bash
$ python -m pip install -r requirements.txt

```
### Option: Using a Service Account
1. Download the credentials.json for your service account.
1. Modify and load setup.bash.
```bash
$ source setup.bash
```

## Usage

1. To add a Nogizaka member's calendar, run the following command:
```
$ python run.py --name (member_name_kn) --en_name (member_name_en) [--is_sa]
```
Include the --is_sa option if you are using a service account.


