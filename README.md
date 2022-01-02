1. [ Testowanie i Prezentacja ]( #test )
2. [ Model danych ]( #model )
3. [ Schemat działania aplikacji ]( #schemat )

<a name="test"></a>
## 1. Testowanie i Prezentacja
Ze względu na użycie biblioteki `channels` tesy nie działają dla SQLite3.

W celach prezentacji nakezy użyć `dummyPLC.py`. Który symuluje server PLC ModbusTCP.

<a name="model"></a>
## 2. Model danych

![Model danych](readme_images/scheme.png)

<a name="model"></a>
## 3. Schemat dizałania aplikacji

### Otwarcie panelu
![Otwarcie panelu](readme_images/connection.png)
### Przycisk Start
![Przycisk Start](readme_images/start.png)
### Przycisk Stop
![Przycisk Stop](readme_images/stop.png)
### Cykliczny update co 500ms
![Cykliczny update co 500ms](readme_images/update.png)