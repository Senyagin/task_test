import pandas as pd

#Импорт файлов формата csv
report = pd.read_csv('initial data/vat_report.csv')
invoices = pd.read_csv('initial data/invoices.csv')
#Преобразуем дату в нужный формат
invoices["Период"] = pd.to_datetime(invoices["Дата ЭСФ"]).dt.strftime("%Y%m").astype(str).astype(int)
#Группируем таблицу и суммируем повторяющиеся элементы
x = invoices.groupby(['Период', 'ИНН Продавца'])['Сумма НДС'].sum().reset_index()
y = report.groupby(['Период', 'ИНН'])['НДС'].sum().reset_index()
#Переименовываем столбец для слияния двух таблиц
x = x.rename(columns={'ИНН Продавца': 'ИНН'})
#Слияние
q = x.merge(y, on=['Период', 'ИНН'], how='outer')
#Пустые значения заполняем нулями
q = q.fillna(0).astype(int)
#Создаем новый столбец для поиска расхождений
q['Сумма расхождений по НДС'] = pd.Series.abs(q['Сумма НДС'] - q['НДС'])
#Получаем нужное расхождение по сумме НДС
q = q[q['Сумма расхождений по НДС'] > 0]
#Делаем тоже самое для поиска расхождений по зачету НДС
a = invoices.groupby(['Период', 'ИНН Покупателя'])['Сумма НДС'].sum().reset_index()
b = report.groupby(['Период', 'ИНН'])['НДС к зачету'].sum().reset_index()
a = a.rename(columns={'ИНН Покупателя': 'ИНН'})
z = a.merge(b, on=['Период', 'ИНН'], how='outer')
z = z.fillna(0).astype(int)
z = (z[z['НДС к зачету'] > z['Сумма НДС']])
z['Сумма расхождений по зачету'] = pd.Series.abs(z['НДС к зачету'] - z['Сумма НДС'])
#Переопределяем переменные для получения нужных столбцов в двух таблицах
z = z[['Период', 'ИНН', 'Сумма расхождений по зачету']]
q = q[['Период', 'ИНН', 'Сумма расхождений по НДС']]
#Объеденяем две таблицы
result = pd.concat([q, z], axis=0, sort=True, ignore_index=True).astype('Int64')
#Выводим результат в файл expected_test.csv
result.fillna(0).sort_values(by=['Период', 'ИНН']).to_csv('actual csv/expected.csv', index=False)
