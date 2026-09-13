"""Fetch the same public news feed used by Sina's 7x24 page; forward minimal metadata."""
import os,json,ssl,urllib.request,urllib.error,html,re,hashlib,hmac,time,uuid,sys
from datetime import datetime
URL='https://app.cj.sina.com.cn/api/news/pc'
def context():
 return ssl.create_default_context(cafile='/etc/ssl/cert.pem' if os.path.exists('/etc/ssl/cert.pem') else None)
class NoRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,*args,**kwargs):return None
def collect():
 req=urllib.request.Request(URL,headers={'User-Agent':'PublicNewsTracker/1.0','Referer':'https://finance.sina.com.cn/7x24/'})
 with urllib.request.urlopen(req,context=context(),timeout=25) as r:d=json.load(r)
 rows=d['result']['data']['feed']['list'];out=[]
 for row in rows[:100]:
  plain=html.unescape(re.sub('<[^>]+>','',row['rich_text'])).strip()
  title=re.match(r'^【([^】]+)】',plain)
  headline=title[1] if title else re.split('[。！？\n]',plain)[0]
  ext=json.loads(row.get('ext') or '{}');url=ext.get('docurl') or row.get('docurl')
  if not url or not url.startswith('https://'):continue
  published=datetime.fromisoformat(row['create_time'].replace(' ','T')+'+08:00').isoformat()
  out.append({'id':'sina-'+str(row['id']),'title':headline[:180],'summary':plain[:220] if title else '', 'source':'新浪财经','publishedAt':published,'url':url,'kind':'报道'})
 if not out:raise ValueError('Feed returned no usable articles')
 return out

def deliver(payload,config=None):
 c=config or {'url':os.environ['DESK_URL'],'siteToken':os.environ['SITES_TOKEN'],'news':os.environ['NEWS_SIGNING_SECRET']}
 raw=json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode();at=str(int(time.time()*1000));nonce=str(uuid.uuid4())
 sig=hmac.new(c['news'].encode(),at.encode()+b'\n'+nonce.encode()+b'\n'+raw,hashlib.sha256).hexdigest()
 req=urllib.request.Request(c['url'].rstrip('/')+'/api/machine',data=raw,headers={'Content-Type':'application/json','OAI-Sites-Authorization':'Bearer '+c['siteToken'],'x-desk-scope':'news','x-desk-time':at,'x-desk-nonce':nonce,'x-desk-signature':sig})
 opener=urllib.request.build_opener(urllib.request.HTTPSHandler(context=context()),NoRedirect())
 with opener.open(req,timeout=30) as r:return json.load(r)

def main():
 try:items=collect()
 except Exception:
  try:deliver({'items':[],'error':'公开新闻源读取失败；保留上次数据。'})
  except Exception:pass
  print('News source unavailable; last successful data preserved',file=sys.stderr);return 1
 if '--check' in sys.argv:
  print(json.dumps({'count':len(items),'latest':items[0]['publishedAt'],'source':'Sina public feed'}));return 0
 try:result=deliver({'items':items});print(json.dumps({'delivered':result.get('count'),'checkedAt':datetime.now().isoformat()}));return 0
 except Exception:print('Delivery failed; inspect service configuration without printing secrets',file=sys.stderr);return 1
if __name__=='__main__':sys.exit(main())
