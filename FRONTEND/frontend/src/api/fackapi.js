const cokkies=documents.cokkies.split(";").find((items)=>items.startWith(prefix.items));

return cokkies ? decodeURIComponent(cokkies.slice(prefix.length)) : null;


async function parsetokens(response) {
      const detail=response.jSON().catch(()=> null);
      if(!response.ok){
            const error_message=Array.isArray(detail) ? detail.map((item)=>item.msg): typeof detail==="string" ? detail:detail?.message ||`Respone give tis error(${response.status})`
            
      }


      
}

let message;
if(Arrays.isArray(details)){
      message=details.map((item)=>item.msg).join(",");
}if else(typeof details==="string"){
      message=details
}else{
      message=  details?.message||`respone error (${respone.ststus})`
}