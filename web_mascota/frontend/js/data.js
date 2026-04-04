// ── Fuente única de datos de productos ─────────────────
// Usada por catalog.html. Mismos datos que index.html.

export const PRODS = [
  { id:1,  name:'Collar ajustable Premium',      category:'perros',    tags:['perros','descuentos'],          price:890,  old_price:1270, badge:'descuento', rating:4 },
  { id:2,  name:'Juguete ratón interactivo',      category:'gatos',     tags:['gatos','nuevo'],                price:650,  old_price:null, badge:'nuevo',     rating:5 },
  { id:3,  name:'Cama ortopédica grande',         category:'perros',    tags:['perros','descuentos'],          price:2490, old_price:3500, badge:'descuento', rating:5 },
  { id:4,  name:'Alimento premium adulto',        category:'perros',    tags:['perros','descuentos'],          price:1350, old_price:1800, badge:'descuento', rating:4 },
  { id:5,  name:'Arena sanitaria premium 5kg',    category:'sanitaria', tags:['gatos','sanitaria','nuevo'],    price:780,  old_price:null, badge:'nuevo',     rating:4 },
  { id:6,  name:'Correa retráctil 5m',            category:'perros',    tags:['perros'],                       price:1100, old_price:null, badge:'hoy',       rating:4 },
  { id:7,  name:'Shampoo hipoalergénico',         category:'shampoo',   tags:['perros','gatos','shampoo'],     price:540,  old_price:null, badge:'hoy',       rating:4 },
  { id:8,  name:'Snacks premio pollo',            category:'perros',    tags:['perros','nuevo'],               price:420,  old_price:null, badge:'nuevo',     rating:5 },
  { id:9,  name:'Transportín mediano',            category:'perros',    tags:['perros','gatos','descuentos'],  price:3200, old_price:4500, badge:'descuento', rating:4 },
  { id:10, name:'Rascador con cama gato',         category:'gatos',     tags:['gatos','nuevo'],                price:1890, old_price:null, badge:'nuevo',     rating:5 },
  { id:11, name:'Clicker educador pro',           category:'educadores',tags:['perros','educadores','descuentos'], price:380, old_price:550, badge:'descuento', rating:4 },
  { id:12, name:'Comedero doble acero',           category:'perros',    tags:['perros','gatos'],               price:680,  old_price:null, badge:'hoy',       rating:4 },
  { id:13, name:'Shampoo de avena gatos',         category:'shampoo',   tags:['gatos','shampoo','nuevo'],      price:590,  old_price:null, badge:'nuevo',     rating:4 },
  { id:14, name:'Jaula premium hámster',          category:'roedores',  tags:['roedores','nuevo'],             price:1800, old_price:null, badge:'nuevo',     rating:5 },
  { id:15, name:'Collar educador seguro',         category:'educadores',tags:['perros','educadores'],          price:950,  old_price:null, badge:'hoy',       rating:4 },
  { id:16, name:'Arena sin olor 6kg',             category:'sanitaria', tags:['gatos','sanitaria','descuentos'], price:1100, old_price:1450, badge:'descuento', rating:4 },
  { id:17, name:'Shampoo anti-pulgas',            category:'shampoo',   tags:['perros','shampoo','descuentos'], price:490,  old_price:680, badge:'descuento', rating:4 },
  { id:18, name:'Kit acuario iniciación',         category:'acuario',   tags:['acuario','nuevo'],              price:3500, old_price:null, badge:'nuevo',     rating:5 },
  { id:19, name:'Rueda ejercicio silenciosa',     category:'roedores',  tags:['roedores','descuentos'],        price:650,  old_price:900,  badge:'descuento', rating:4 },
  { id:20, name:'Alimento balanceado conejo',     category:'roedores',  tags:['roedores','nuevo'],             price:520,  old_price:null, badge:'nuevo',     rating:4 },
  { id:21, name:'Jaula grande conejos',           category:'roedores',  tags:['roedores'],                     price:4200, old_price:null, badge:'hoy',       rating:4 },
  { id:22, name:'Alimento mixto aves',            category:'roedores',  tags:['roedores','descuentos'],        price:380,  old_price:520,  badge:'descuento', rating:4 },
  { id:23, name:'Filtro acuario externo',         category:'acuario',   tags:['acuario'],                      price:1900, old_price:null, badge:'hoy',       rating:4 },
  { id:24, name:'Pipeta antiparasitaria gato',    category:'gatos',     tags:['gatos','descuentos'],           price:820,  old_price:1100, badge:'descuento', rating:4 },
];

// ── Filtro local (sin API) ─────────────────────────────
export function filterProducts({ category = '', tag = '', search = '' } = {}) {
  return PRODS.filter(p => {
    if (category && p.category !== category) return false;
    if (tag      && !p.tags.includes(tag))   return false;
    if (search   && !p.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });
}
