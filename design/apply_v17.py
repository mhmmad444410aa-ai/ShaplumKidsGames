from pathlib import Path
import re, json
from xml.sax.saxutils import escape
root=Path("app/src/main")
settings=Path("settings.gradle.kts")
s=settings.read_text()
assert "repositories { google(); mavenCentral() }" in s
settings.write_text(s.replace("repositories { google(); mavenCentral() }",'repositories { google(); mavenCentral(); maven { url = uri("https://developer.huawei.com/repo/") } }'))
g=Path("app/build.gradle.kts")
s=g.read_text()
s=re.sub(r'versionCode\s*=\s*\d+', "versionCode = 8",s,count=1)
s=re.sub(r'versionName\s*=\s*"[^"]+"','versionName = "1.7.0"',s,count=1)
s=re.sub(r'(?m)^\s*buildConfigField\("String", "HUAWEI_BANNER_ID".*$', '        buildConfigField("String", "HUAWEI_BANNER_ID", safeQuoted("c9uhivwtc2"))\n        buildConfigField("String", "HUAWEI_INTERSTITIAL_ID", safeQuoted("g3b44r11ew"))',s)
s=s.replace('buildConfigField("boolean", "ADS_ENABLED", "false")','buildConfigField("boolean", "ADS_ENABLED", "true")')
s=s.replace('providers.environmentVariable("PRIVACY_POLICY_URL").orElse("").get()','providers.environmentVariable("PRIVACY_POLICY_URL").orElse("https://github.com/mhmmad444410aa-ai/ShaplumKidsGames/blob/main/PRIVACY.md").get()')
s=s.replace('dependencies {','dependencies {\n    implementation("com.huawei.hms:ads-prime:3.4.91.300")',1)
assert 'c9uhivwtc2' in s and 'g3b44r11ew' in s
g.write_text(s)
p=Path("app/proguard-rules.pro")
p.write_text(p.read_text()+"\n-keep class com.huawei.openalliance.ad.** { *; }\n-keep class com.huawei.hms.ads.** { *; }\n")
p=root/"AndroidManifest.xml"
s=p.read_text().replace('xmlns:android="http://schemas.android.com/apk/res/android"','xmlns:android="http://schemas.android.com/apk/res/android" xmlns:tools="http://schemas.android.com/tools"')
s=s.replace('<!-- Intentionally no INTERNET, advertising ID, storage, or dangerous permissions. -->','''<!-- Network only for disclosed parent-area advertising. Remove identifier and location permissions from dependency manifests. -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <!-- SDK may post download notifications. App never requests this runtime permission. -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="com.google.android.gms.permission.AD_ID" tools:node="remove" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" tools:node="remove" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" tools:node="remove" />
    <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" tools:node="remove" />''')
assert "android.permission.INTERNET" in s
p.write_text(s)
ui=root/"java/com/mhmmad/shaplumkidsgames/ui"
(ui/"ParentAds.kt").write_text((Path("../design/ParentAds.kt")).read_text(),encoding="utf-8")
p=ui/"App.kt"
s=p.read_text()
anchor='ActionButton(stringResource(R.string.about),{vm.navigate(Page.ABOUT)},Modifier.fillMaxWidth(),Symbol.HOME,Purple,"about")'
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'\n            if(s.page==Page.PARENTS) ParentAdPanel({vm.navigate(Page.PROGRESS)},{vm.navigate(Page.ABOUT)})')
p.write_text(s)
locales=json.loads("{\"values\":{\"parent_info\":\"Made for ages 4–8. Game progress stays on this device. Ads, if available, are restricted to the parent area after guardian privacy consent.\",\"privacy_text\":\"Game progress and preferences are stored locally. No ads are requested before guardian consent. Petal Ads requests in the parent area are configured as child-directed, non-personalised and rated W. Read the full privacy policy for details. You can withdraw consent in the parent area or clear app data.\",\"version_label\":\"Version 1.7.0\",\"guardian_ad_privacy\":\"For parents and guardians only: this area can use Petal Ads to display non-personalised, child-safe advertising. Please read the privacy policy before giving consent. The games remain available without consent.\",\"guardian_privacy_accept\":\"I am a parent or guardian and agree to the privacy notice\",\"guardian_privacy_withdraw\":\"Withdraw privacy consent\",\"guardian_activity_summary\":\"View activity summary\",\"guardian_ad_label\":\"Advertisement\"},\"values-ar\":{\"parent_info\":\"مصممة للأعمار ٤–٨ سنوات. يُحفظ تقدم اللعب على الجهاز. تقتصر الإعلانات المتاحة على قسم أولياء الأمور بعد الموافقة على الخصوصية.\",\"privacy_text\":\"يُحفظ تقدم اللعب والتفضيلات محليًا. لا تُطلب الإعلانات قبل موافقة ولي الأمر. تُضبط طلبات Petal Ads في قسم أولياء الأمور لتكون غير مخصصة وموجهة لحماية الأطفال بتصنيف W. راجع سياسة الخصوصية الكاملة، ويمكن سحب الموافقة في قسم أولياء الأمور أو مسح بيانات التطبيق.\",\"version_label\":\"الإصدار 1.7.0\",\"guardian_ad_privacy\":\"لأولياء الأمور فقط: قد يستخدم هذا القسم Petal Ads لعرض إعلانات غير مخصصة بتصنيف مناسب للأطفال. اقرأ سياسة الخصوصية قبل الموافقة. تبقى الألعاب متاحة دون موافقة.\",\"guardian_privacy_accept\":\"أنا ولي أمر وأوافق على إشعار الخصوصية\",\"guardian_privacy_withdraw\":\"سحب الموافقة على الخصوصية\",\"guardian_activity_summary\":\"عرض ملخص النشاط\",\"guardian_ad_label\":\"إعلان\"},\"values-pt-rBR\":{\"parent_info\":\"Para crianças de 4 a 8 anos. O progresso fica no dispositivo. Os anúncios disponíveis ficam restritos à área dos responsáveis após o consentimento de privacidade.\",\"privacy_text\":\"O progresso e as preferências são armazenados localmente. Nenhum anúncio é solicitado antes do consentimento do responsável. As solicitações Petal Ads na área dos responsáveis são configuradas para proteção infantil, sem personalização e com classificação W. Consulte a política completa. É possível retirar o consentimento na área dos responsáveis ou limpar os dados do aplicativo.\",\"version_label\":\"Versão 1.7.0\",\"guardian_ad_privacy\":\"Somente para responsáveis: esta área pode usar Petal Ads para exibir anúncios não personalizados com classificação adequada para crianças. Leia a política de privacidade antes de consentir. Os jogos continuam disponíveis sem consentimento.\",\"guardian_privacy_accept\":\"Sou responsável e concordo com o aviso de privacidade\",\"guardian_privacy_withdraw\":\"Retirar consentimento de privacidade\",\"guardian_activity_summary\":\"Ver resumo de atividades\",\"guardian_ad_label\":\"Publicidade\"},\"values-en-rGB\":{\"parent_info\":\"Made for ages 4–8. Game progress stays on this device. Ads, if available, are restricted to the parent area after guardian privacy consent.\",\"privacy_text\":\"Game progress and preferences are stored locally. No ads are requested before guardian consent. Petal Ads requests in the parent area are configured as child-directed, non-personalised and rated W. Read the full privacy policy for details. You can withdraw consent in the parent area or clear app data.\",\"version_label\":\"Version 1.7.0\",\"guardian_ad_privacy\":\"For parents and guardians only: this area can use Petal Ads to display non-personalised, child-safe advertising. Please read the privacy policy before giving consent. The games remain available without consent.\",\"guardian_privacy_accept\":\"I am a parent or guardian and agree to the privacy notice\",\"guardian_privacy_withdraw\":\"Withdraw privacy consent\",\"guardian_activity_summary\":\"View activity summary\",\"guardian_ad_label\":\"Advertisement\"}}")
for locale,values in locales.items():
    p=root/"res"/locale/"strings.xml";s=p.read_text()
    for key,value in values.items():
        e='<string name="'+key+'">'+escape(value)+'</string>'
        pattern=r'<string name="'+key+r'">.*?</string>'
        if re.search(pattern,s,flags=re.S): s=re.sub(pattern,lambda m:e,s,flags=re.S)
        else: s=s.replace("</resources>","    "+e+"\n</resources>")
    p.write_text(s)
p=Path("tools/verify_resources.py");s=p.read_text()
s=s.replace("assert not manifest.findall('uses-permission'),'Unexpected permission'","""ns='{http://schemas.android.com/apk/res/android}'
tools='{http://schemas.android.com/tools}'
perms={e.attrib.get(ns+'name') for e in manifest.findall('uses-permission') if e.attrib.get(tools+'node')!='remove'}
assert perms=={'android.permission.INTERNET','android.permission.ACCESS_NETWORK_STATE','android.permission.POST_NOTIFICATIONS'},f'Unexpected permissions: {perms}'""")
s=s.replace("no permissions or signing files","only declared network and SDK notification permissions; no signing files")
p.write_text(s)
print("Applied 1.7 Petal Ads, guardian-only placement, consent lifecycle, privacy resources and test IDs.")
