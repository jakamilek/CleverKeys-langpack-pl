package tribixbite.cleverkeys.langpack
import java.io.File
import java.util.zip.ZipFile
import tribixbite.cleverkeys.swipe.geometric.CkdtDictionaryReader
object ApprovedPracticalConsumerCheck {
 fun pack(path:String,previous:LanguageIntelligenceProvider?=null):LanguageIntelligenceProvider=ZipFile(path).use { z ->
  val m=z.getInputStream(z.getEntry("manifest.json")).reader(Charsets.UTF_8).use(IntelligenceJson::document)
  val d=IntelligenceJson.declaration(m)!!
  z.getInputStream(z.getEntry(d.file)).reader(Charsets.UTF_8).use { IntelligenceJson.parse(it,"pl",IntelligenceJson.integer(m,"version"),IntelligenceJson.capabilities(m),previous,d.schemaVersion) }
 }
 @JvmStatic fun main(args:Array<String>) {
  val mode=args[0];val low=mode!="full";if(low)check(Runtime.getRuntime().maxMemory()<=192L*1024*1024)
  val ballast=if(low)ByteArray(16*1024*1024) else null
  val old=when(mode){"cold"->null;"repeat"->pack(args[2]);else->pack(args[1])}
  val updated=pack(args[2],old);check(updated.packageInfo().version==13)
  old?.sharedSources?.let { check(updated.sharedSources!!.extendsTables(it)) }
  val keys=File(args[3]).readLines();check(keys.size==1087)
  for(k in keys)check(updated.lookup(k)?.sourceLemmas?.isNotEmpty()==true){"Missing added metadata: $k"}
  for((a,b) in listOf("powerbank" to "powerbanki","streaming" to "streamingu","googlować" to "googluje","streamować" to "streamuje"))check(updated.sharesSourceLemma(a,b))
  check(!updated.sharesSourceLemma("streaming","streamować"))
  if(mode=="full") {
   fun words(path:String)=ZipFile(path).use {z->CkdtDictionaryReader.readEntries(z.getInputStream(z.getEntry("dictionary.bin")).readBytes())}
   val before=words(args[1]);val after=words(args[2]);check(before.size==204463 && after.size==205550)
   val oldKeys=before.map {it.word}.toSet()
   check(after.filter {it.word in oldKeys}==before){"Changed old CKDT records or relative rank order"}
   check(after.filter {it.word !in oldKeys}.map {it.word}.toSet()==keys.toSet())
   val cold=pack(args[2]);var retained=0
   for(w in before) {
    val e=old!!.lookup(w.word);check(e==cold.lookup(w.word)){"Changed cold metadata: ${w.word}"}
    check(e==updated.lookup(w.word));if(e!=null){check(e===updated.lookup(w.word));retained++}
   }
   check(retained==114299)
   for(k in keys){check(old!!.lookup(k)==null);check(cold.lookup(k)==updated.lookup(k))}
   println("PASS full: 204463 old words/ranks, 114299 old cold metadata and reused objects; 1087 additions; accepted v11 readers")
  } else {check(ballast!!.first()==0.toByte() && ballast.last()==0.toByte());println("PASS $mode: actual reader, 192 MiB heap and 16 MiB ballast; not phone RAM")}
 }
}
