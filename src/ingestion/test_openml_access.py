import openml
from openml.exceptions import OpenMLServerError


FREQUENCY_DATASET_ID = 41214


try:
    dataset = openml.datasets.get_dataset(
        FREQUENCY_DATASET_ID,
        download_data=False,
    )

except OpenMLServerError:
    print("OpenML sunucusuna şu anda erişilemiyor.")
    print("Dataset ID:", FREQUENCY_DATASET_ID)
    print("İşlem başarısız oldu ancak program kontrollü şekilde sonlandı.")

else:
    print("OpenML bağlantısı başarılı.")
    print("Dataset name:", dataset.name)
    print("Dataset version:", dataset.version)