hissedataproducer.py her gün çalıştırılacak böylece her gün son 400 günlük data elde edilecek. Bunu daha sonradan server.py ya da zamanlayıcı ile tetiklenecek hale getirebiliriz. Bu kod her gün için hissedata.db yi oluşturacak.
İlk çalıştığında 400 günü sonraki çalıştığında sonraki verileri ekleyecek.

Sonra güncel verilerle ma_lists.py çalıştırılacak.

Tek kullanımlık kodla signals.db oluşturuldu. İçeriği ma_lists.py ile dolduruldu. 